"""
oidc_client.py  --  Keycloak OIDC integration module (Python / authlib + httpx)
Project: VibeCodeProjects / KH-Sim  |  Task: AUTH-003

Provides two integration patterns:

  1. Authorization Code + PKCE S256  (browser-facing flows)
     Client:      kh-sim-spa (public, no secret)
     Entry points: generate_pkce_params(), build_auth_url(), exchange_code()

  2. Client Credentials grant  (M2M -- server-to-server)
     Client:      kh-py-svc (confidential)
     Entry points: get_m2m_token()

  Shared utilities:
     discover()               -- OIDC metadata fetch (cached after first call)
     validate_token_local()   -- local JWT signature + claims validation via JWKS
     introspect()             -- token introspection via Keycloak endpoint (network)
     is_keycloak_reachable()  -- lightweight health probe (no-throw)

Keycloak realm   : vibedev
Host port        : 8090  (docker-compose.r0-lde.yml)
Discovery URL    : http://localhost:8090/realms/vibedev/.well-known/openid-configuration

Dependencies:
    authlib >= 1.3.0     pip install "authlib>=1.3.0"
    httpx   >= 0.27.0    pip install "httpx>=0.27.0"

    See kh-sim/auth/python/requirements.txt for pinned versions.

Environment variables  (all have LDE-safe defaults):
    KC_BASE_URL              base URL of Keycloak  (default: http://localhost:8090)
    KC_REALM                 realm name            (default: vibedev)
    KC_SPA_CLIENT_ID         SPA client ID         (default: kh-sim-spa)
    KC_SPA_REDIRECT_URI      OAuth callback URI    (default: http://localhost:3000/callback)
    KC_PY_SVC_CLIENT_ID      M2M client ID         (default: kh-py-svc)
    KC_PY_SVC_SECRET         M2M client secret     (required for M2M; no default)

FastAPI usage example -- PKCE flow::

    from fastapi import FastAPI, Request
    from fastapi.responses import RedirectResponse
    import kh_sim.auth.python.oidc_client as oidc

    app = FastAPI()

    @app.get("/login")
    async def login(request: Request):
        params = oidc.generate_pkce_params()
        request.session["code_verifier"] = params["code_verifier"]
        result = await oidc.build_auth_url(params["code_challenge"])
        request.session["state"] = result["state"]
        return RedirectResponse(result["auth_url"])

    @app.get("/callback")
    async def callback(request: Request, code: str, state: str):
        token_set = await oidc.exchange_code(
            code=code,
            state=state,
            expected_state=request.session["state"],
            code_verifier=request.session["code_verifier"],
        )
        request.session["access_token"] = token_set["access_token"]
        return {"authenticated": True}

M2M usage example::

    import kh_sim.auth.python.oidc_client as oidc

    token = await oidc.get_m2m_token()
    headers = {"Authorization": f"Bearer {token}"}

Middleware example (JWT Bearer validation)::

    from fastapi import Depends, HTTPException, Security
    from fastapi.security import HTTPBearer

    bearer = HTTPBearer()

    async def require_token(credentials = Security(bearer)):
        claims = await oidc.validate_token_local(credentials.credentials)
        if not claims.get("active", True):   # local validation; active from introspect
            raise HTTPException(status_code=401, detail="Invalid token")
        return claims
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Optional dependencies -- both authlib and httpx are required for OIDC flows.
# Guards follow the same pattern as log_connector.py: fail at call time,
# not at import time, so the module can be imported even in environments
# where the packages are not installed yet.
# ---------------------------------------------------------------------------
try:
    import httpx  # type: ignore
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

try:
    from authlib.jose import JsonWebKeySet, jwt as _authlib_jwt  # type: ignore
    from authlib.integrations.httpx_client import (  # type: ignore
        AsyncOAuth2Client,
        OAuth2Client,
    )
    _AUTHLIB_AVAILABLE = True
except ImportError:
    _AUTHLIB_AVAILABLE = False


def _require_deps() -> None:
    """Raise a clear ImportError if authlib or httpx are missing."""
    missing = []
    if not _HTTPX_AVAILABLE:
        missing.append("httpx>=0.27.0")
    if not _AUTHLIB_AVAILABLE:
        missing.append("authlib>=1.3.0")
    if missing:
        raise ImportError(
            "AUTH-003 oidc_client requires: "
            + ", ".join(missing)
            + ".  Install with: pip install "
            + " ".join(missing)
        )


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

KC_BASE_URL   = os.environ.get("KC_BASE_URL",  "http://localhost:8090")
KC_REALM      = os.environ.get("KC_REALM",     "vibedev")
DISCOVERY_URL = f"{KC_BASE_URL}/realms/{KC_REALM}/.well-known/openid-configuration"

# ---------------------------------------------------------------------------
# Module-level cache: OIDC metadata + JWKS (populated on first call)
# ---------------------------------------------------------------------------
_oidc_metadata: Optional[dict] = None
_jwks_keyset: Any = None   # JsonWebKeySet instance


# ---------------------------------------------------------------------------
# OIDC discovery
# ---------------------------------------------------------------------------

async def discover() -> dict:
    """
    Fetch (and cache) the Keycloak OIDC metadata document.

    Executes one GET to DISCOVERY_URL on first call; subsequent calls return
    the cached dict.  Reset ``_oidc_metadata = None`` to force re-discovery.

    Returns
    -------
    dict
        Parsed OIDC configuration document with keys such as
        ``authorization_endpoint``, ``token_endpoint``, ``jwks_uri``, etc.

    Raises
    ------
    ImportError
        If httpx is not installed.
    httpx.HTTPStatusError
        If Keycloak returns a non-2xx response (e.g. realm not found).
    httpx.ConnectError
        If Keycloak is not reachable at KC_BASE_URL.
    """
    global _oidc_metadata
    _require_deps()
    if _oidc_metadata is not None:
        return _oidc_metadata
    async with httpx.AsyncClient() as client:
        resp = await client.get(DISCOVERY_URL, timeout=8.0)
        resp.raise_for_status()
        _oidc_metadata = resp.json()
    return _oidc_metadata


# ---------------------------------------------------------------------------
# PKCE helpers (Authorization Code + PKCE S256, public client)
# ---------------------------------------------------------------------------

def generate_pkce_params() -> dict[str, str]:
    """
    Generate a PKCE verifier / challenge pair (RFC 7636, method S256).

    Caller MUST persist ``code_verifier`` in the server-side session.
    ``code_challenge`` is included in the authorization redirect URL.
    ``code_verifier`` is sent to the token endpoint during code exchange.

    Returns
    -------
    dict with keys:
        ``code_verifier``   -- 43-char URL-safe random string
        ``code_challenge``  -- SHA-256(verifier), base64url-encoded (no padding)
    """
    code_verifier = secrets.token_urlsafe(32)   # 32 bytes => 43 base64url chars
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return {"code_verifier": code_verifier, "code_challenge": code_challenge}


async def build_auth_url(
    code_challenge: str,
    state: Optional[str] = None,
    nonce: Optional[str] = None,
    scope: str = "openid profile email",
) -> dict[str, str]:
    """
    Build the Keycloak authorization URL for an Auth Code + PKCE S256 flow.

    Keycloak client requirements:
        client_id   : KC_SPA_CLIENT_ID  (default: kh-sim-spa)
        Access Type : public (no secret)
        PKCE        : pkce.code.challenge.method = S256

    Parameters
    ----------
    code_challenge : str
        From ``generate_pkce_params()["code_challenge"]``.
    state : str, optional
        CSRF token.  Auto-generated if omitted; always persist in session.
    nonce : str, optional
        Replay nonce.  Include when consuming ``id_token``.
    scope : str
        Space-separated OIDC scopes (default: "openid profile email").

    Returns
    -------
    dict with keys:
        ``auth_url``  -- Full authorization redirect URL
        ``state``     -- State value (persist in session; validate on callback)
    """
    _require_deps()
    metadata = await discover()
    auth_endpoint = metadata["authorization_endpoint"]

    _state = state or secrets.token_urlsafe(16)
    client_id    = os.environ.get("KC_SPA_CLIENT_ID",   "kh-sim-spa")
    redirect_uri = os.environ.get("KC_SPA_REDIRECT_URI", "http://localhost:3000/callback")

    # Build parameters manually -- no OAuth2Client needed for the redirect URL
    params: dict[str, str] = {
        "response_type":          "code",
        "client_id":              client_id,
        "redirect_uri":           redirect_uri,
        "scope":                  scope,
        "state":                  _state,
        "code_challenge":         code_challenge,
        "code_challenge_method":  "S256",
    }
    if nonce:
        params["nonce"] = nonce

    import urllib.parse
    auth_url = auth_endpoint + "?" + urllib.parse.urlencode(params)
    return {"auth_url": auth_url, "state": _state}


async def exchange_code(
    code: str,
    state: str,
    expected_state: str,
    code_verifier: str,
) -> dict[str, Any]:
    """
    Exchange an authorization code for tokens (PKCE S256 verification).

    Call this in the OAuth callback route handler after receiving ``code``
    and ``state`` query parameters from Keycloak.

    Parameters
    ----------
    code : str
        Authorization code from the callback query string.
    state : str
        ``state`` value from the callback query string.
    expected_state : str
        ``state`` value stored in the user session (CSRF guard).
    code_verifier : str
        Code verifier stored in the user session.

    Returns
    -------
    dict
        Token response from Keycloak, containing at minimum:
        ``access_token``, ``id_token``, ``token_type``, ``expires_in``.

    Raises
    ------
    ValueError
        If ``state`` does not match ``expected_state`` (CSRF mismatch).
    httpx.HTTPStatusError
        If Keycloak returns an error response (e.g. expired code).
    """
    _require_deps()
    if state != expected_state:
        raise ValueError(
            f"OIDC state mismatch -- possible CSRF attempt. "
            f"expected={expected_state!r}  received={state!r}"
        )
    metadata     = await discover()
    token_url    = metadata["token_endpoint"]
    client_id    = os.environ.get("KC_SPA_CLIENT_ID",   "kh-sim-spa")
    redirect_uri = os.environ.get("KC_SPA_REDIRECT_URI", "http://localhost:3000/callback")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            token_url,
            data={
                "grant_type":    "authorization_code",
                "client_id":     client_id,
                "redirect_uri":  redirect_uri,
                "code":          code,
                "code_verifier": code_verifier,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Client Credentials (M2M, confidential client)
# ---------------------------------------------------------------------------

async def get_m2m_token(scope: Optional[str] = None) -> str:
    """
    Obtain an M2M access token via the Client Credentials grant.

    The token is NOT cached here -- caller may cache with expiry if desired.
    Typical ``access_token`` lifetime: 300 s (Keycloak vibedev realm default).

    Keycloak client requirements:
        client_id     : KC_PY_SVC_CLIENT_ID  (default: kh-py-svc)
        Access Type   : confidential
        Service Accts : enabled
        Standard Flow : disabled

    KC_PY_SVC_SECRET must be set to the client secret from the Keycloak
    Admin UI (Clients > kh-py-svc > Credentials tab).

    Parameters
    ----------
    scope : str, optional
        Additional scopes to request; omit for realm-default scopes.

    Returns
    -------
    str
        Raw access token string for use in ``Authorization: Bearer <token>`` headers.

    Raises
    ------
    EnvironmentError
        If KC_PY_SVC_SECRET is not set.
    httpx.HTTPStatusError
        If Keycloak rejects the credentials.
    """
    _require_deps()
    client_id     = os.environ.get("KC_PY_SVC_CLIENT_ID", "kh-py-svc")
    client_secret = os.environ.get("KC_PY_SVC_SECRET")
    if not client_secret:
        raise EnvironmentError(
            "KC_PY_SVC_SECRET is not set. "
            "Obtain the client secret from Keycloak Admin UI: "
            f"{KC_BASE_URL}/admin/master/console/#/{KC_REALM}/clients"
        )

    metadata  = await discover()
    token_url = metadata["token_endpoint"]

    payload: dict[str, str] = {
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
    }
    if scope:
        payload["scope"] = scope

    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=payload, timeout=10.0)
        resp.raise_for_status()
        return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# JWT validation -- local JWKS signature + claims check
# ---------------------------------------------------------------------------

async def _get_jwks() -> Any:
    """Fetch (and cache) the Keycloak JWKS key set."""
    global _jwks_keyset
    if _jwks_keyset is not None:
        return _jwks_keyset
    metadata = await discover()
    jwks_uri = metadata["jwks_uri"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_uri, timeout=8.0)
        resp.raise_for_status()
        _jwks_keyset = JsonWebKeySet.import_key_set(resp.json())
    return _jwks_keyset


async def validate_token_local(
    access_token: str,
    audience: Optional[str] = None,
) -> dict[str, Any]:
    """
    Validate an access token locally using Keycloak's JWKS endpoint.

    Performs signature verification + standard claims validation
    (``exp``, ``iat``, ``iss``).  Does NOT contact the introspection endpoint
    -- use ``introspect()`` if revocation checking is required.

    JWKS key set is cached after the first call.  Reset ``_jwks_keyset = None``
    to force a JWKS refresh (e.g. after a Keycloak key rotation).

    Parameters
    ----------
    access_token : str
        Bearer token string to validate.
    audience : str, optional
        Expected ``aud`` claim value.  If omitted, audience check is skipped.

    Returns
    -------
    dict
        Decoded JWT claims (``sub``, ``realm_access``, ``preferred_username``,
        ``exp``, ``iat``, ``iss``, etc.).

    Raises
    ------
    authlib.jose.errors.JoseError
        On signature failure, expiry, issuer mismatch, or audience mismatch.
    """
    _require_deps()
    keyset = await _get_jwks()
    issuer = f"{KC_BASE_URL}/realms/{KC_REALM}"

    claims_options: dict[str, Any] = {
        "iss": {"essential": True, "value": issuer},
        "exp": {"essential": True},
    }
    if audience:
        claims_options["aud"] = {"essential": True, "value": audience}

    claims = _authlib_jwt.decode(access_token, keyset, claims_options=claims_options)
    claims.validate()
    return dict(claims)


# ---------------------------------------------------------------------------
# Token introspection (network round-trip; revocation-aware)
# ---------------------------------------------------------------------------

async def introspect(
    access_token: str,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> dict[str, Any]:
    """
    Introspect an access token at the Keycloak introspection endpoint (RFC 7662).

    Uses the M2M confidential client (kh-py-svc) as the introspecting party.
    Returns the full introspection response:
        ``{ "active": true,  "sub": ..., "realm_access": ..., ... }``
        ``{ "active": false }``  -- expired or revoked token

    Use this in API middleware when revocation checking is required and
    local JWKS signature validation alone is insufficient.

    Parameters
    ----------
    access_token : str
        Bearer token to introspect.
    client_id : str, optional
        Introspecting client ID; defaults to KC_PY_SVC_CLIENT_ID.
    client_secret : str, optional
        Introspecting client secret; defaults to KC_PY_SVC_SECRET.

    Returns
    -------
    dict
        RFC 7662 introspection response object.

    Raises
    ------
    EnvironmentError
        If client secret is not available.
    httpx.HTTPStatusError
        If Keycloak returns a non-2xx response.
    """
    _require_deps()
    _client_id     = client_id     or os.environ.get("KC_PY_SVC_CLIENT_ID", "kh-py-svc")
    _client_secret = client_secret or os.environ.get("KC_PY_SVC_SECRET")
    if not _client_secret:
        raise EnvironmentError(
            "KC_PY_SVC_SECRET is not set -- required for token introspection."
        )

    metadata         = await discover()
    introspection_url = metadata["introspection_endpoint"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            introspection_url,
            data={"token": access_token},
            auth=(_client_id, _client_secret),
            timeout=8.0,
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Health probe
# ---------------------------------------------------------------------------

async def is_keycloak_reachable() -> bool:
    """
    Lightweight connectivity probe: attempts OIDC discovery against Keycloak.

    Resets the discovery cache so a previously failed discovery is retried.
    Returns ``True`` if Keycloak is reachable and the discovery document is
    valid; ``False`` on any network or HTTP error.  Never raises.

    Returns
    -------
    bool
    """
    global _oidc_metadata
    _require_deps()
    _oidc_metadata = None   # force fresh probe
    try:
        await discover()
        return True
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# Synchronous convenience wrappers
# (for scripts and pytest fixtures that are not running an event loop)
# ---------------------------------------------------------------------------

def discover_sync() -> dict:
    """Synchronous wrapper around ``discover()``."""
    import asyncio
    return asyncio.run(discover())


def get_m2m_token_sync(scope: Optional[str] = None) -> str:
    """Synchronous wrapper around ``get_m2m_token()``."""
    import asyncio
    return asyncio.run(get_m2m_token(scope))


def validate_token_local_sync(
    access_token: str,
    audience: Optional[str] = None,
) -> dict[str, Any]:
    """Synchronous wrapper around ``validate_token_local()``."""
    import asyncio
    return asyncio.run(validate_token_local(access_token, audience))


def introspect_sync(access_token: str) -> dict[str, Any]:
    """Synchronous wrapper around ``introspect()``."""
    import asyncio
    return asyncio.run(introspect(access_token))


def is_keycloak_reachable_sync() -> bool:
    """Synchronous wrapper around ``is_keycloak_reachable()``."""
    import asyncio
    return asyncio.run(is_keycloak_reachable())


# ---------------------------------------------------------------------------
# Module-level exports summary
# ---------------------------------------------------------------------------
__all__ = [
    # OIDC discovery
    "discover",
    "discover_sync",
    # PKCE (Auth Code + PKCE S256)
    "generate_pkce_params",
    "build_auth_url",
    "exchange_code",
    # M2M (Client Credentials)
    "get_m2m_token",
    "get_m2m_token_sync",
    # JWT validation (local JWKS)
    "validate_token_local",
    "validate_token_local_sync",
    # Introspection (network, revocation-aware)
    "introspect",
    "introspect_sync",
    # Health
    "is_keycloak_reachable",
    "is_keycloak_reachable_sync",
    # Config constants
    "KC_BASE_URL",
    "KC_REALM",
    "DISCOVERY_URL",
]
