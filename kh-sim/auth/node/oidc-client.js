'use strict';
/**
 * kh-sim/auth/node/oidc-client.js
 * AUTH-002 -- Keycloak OIDC integration module (openid-client v5 / PKCE S256)
 *
 * Provides two integration patterns:
 *
 *   1. Authorization Code + PKCE S256
 *      Client: kh-sim-spa (public, no secret)
 *      Use case: browser SPA login; server-side code exchange
 *      Entry points: generatePkceParams(), buildAuthUrl(), exchangeCode()
 *
 *   2. Client Credentials (M2M)
 *      Client: kh-node-svc (confidential)
 *      Use case: kh-log-service and future Node microservices obtaining Bearer tokens
 *      Entry points: getM2mToken()
 *
 *   Shared:
 *      discoverIssuer()        -- OIDC discovery (cached after first call)
 *      introspect(token)       -- token introspection via Keycloak endpoint
 *      isKeycloakReachable()   -- lightweight health probe
 *
 * Keycloak realm   : vibedev
 * Host port        : 8090  (docker-compose.r0-lde.yml)
 * Discovery URL    : http://localhost:8090/realms/vibedev/.well-known/openid-configuration
 *
 * Dependencies:
 *   openid-client ^5.7.x  -- npm install openid-client
 *
 * Environment variables (all have LDE-safe defaults):
 *   KC_BASE_URL              base URL of Keycloak  (default: http://localhost:8090)
 *   KC_REALM                 realm name            (default: vibedev)
 *   KC_SPA_CLIENT_ID         SPA client ID         (default: kh-sim-spa)
 *   KC_SPA_REDIRECT_URI      OAuth callback URI    (default: http://localhost:3000/callback)
 *   KC_NODE_SVC_CLIENT_ID    M2M client ID         (default: kh-node-svc)
 *   KC_NODE_SVC_SECRET       M2M client secret     (required for M2M flows; no default)
 *
 * Usage example -- PKCE flow (Express):
 *   const oidc = require('./oidc-client');
 *
 *   app.get('/login', async (req, res) => {
 *     const { codeVerifier, codeChallenge } = oidc.generatePkceParams();
 *     req.session.codeVerifier = codeVerifier;
 *     const { authUrl, state } = await oidc.buildAuthUrl(codeChallenge);
 *     req.session.state = state;
 *     res.redirect(authUrl);
 *   });
 *
 *   app.get('/callback', async (req, res) => {
 *     const tokenSet = await oidc.exchangeCode(
 *       req.url, req.session.state, req.session.codeVerifier
 *     );
 *     req.session.accessToken = tokenSet.access_token;
 *     res.redirect('/');
 *   });
 *
 * Usage example -- M2M token:
 *   const oidc = require('./oidc-client');
 *   const token = await oidc.getM2mToken();
 *   // attach as: Authorization: Bearer <token>
 */

const { Issuer, generators } = require('openid-client');

// ── Config ────────────────────────────────────────────────────────────────────
const KC_BASE_URL    = process.env.KC_BASE_URL || 'http://localhost:8090';
const KC_REALM       = process.env.KC_REALM    || 'vibedev';
const DISCOVERY_URL  = `${KC_BASE_URL}/realms/${KC_REALM}/.well-known/openid-configuration`;

// ── Module-level cache (issuer + clients initialised once at startup) ─────────
let _issuer     = null;
let _pkceClient = null;
let _m2mClient  = null;

// ── Issuer discovery ─────────────────────────────────────────────────────────

/**
 * Discover (and cache) the Keycloak OIDC Issuer.
 * Executes one HTTP call to DISCOVERY_URL on first invocation; cached thereafter.
 * Call once at service startup (e.g. in an Express app.listen callback) so the
 * first real request does not incur discovery latency.
 *
 * @returns {Promise<import('openid-client').Issuer>}
 * @throws  If the discovery URL is unreachable (Keycloak not running / wrong port).
 */
async function discoverIssuer() {
  if (_issuer) return _issuer;
  _issuer = await Issuer.discover(DISCOVERY_URL);
  return _issuer;
}

// ── PKCE helpers (Authorization Code + PKCE S256, public client) ─────────────

/**
 * Lazily build (and cache) the public SPA client for kh-sim-spa.
 *
 * Keycloak client registration requirements:
 *   client_id            : kh-sim-spa
 *   Access Type          : public (no client secret)
 *   Standard Flow        : enabled
 *   PKCE enforcement     : pkce.code.challenge.method = S256
 *   Valid redirect URIs  : http://localhost:3000/*
 *
 * @returns {Promise<import('openid-client').Client>}
 */
async function getPkceClient() {
  if (_pkceClient) return _pkceClient;
  const issuer = await discoverIssuer();
  _pkceClient = new issuer.Client({
    client_id:                    process.env.KC_SPA_CLIENT_ID || 'kh-sim-spa',
    redirect_uris:                [process.env.KC_SPA_REDIRECT_URI || 'http://localhost:3000/callback'],
    response_types:               ['code'],
    token_endpoint_auth_method:   'none',   // public client -- no secret
  });
  return _pkceClient;
}

/**
 * Generate a PKCE verifier / challenge pair (RFC 7636, method S256).
 *
 * Caller MUST persist codeVerifier in the user session (server-side).
 * codeChallenge is passed to Keycloak in the authorization redirect URL.
 * codeVerifier is sent to the token endpoint during code exchange.
 *
 * @returns {{ codeVerifier: string, codeChallenge: string }}
 */
function generatePkceParams() {
  const codeVerifier  = generators.codeVerifier();   // 43-128 char random string
  const codeChallenge = generators.codeChallenge(codeVerifier);  // SHA-256, base64url
  return { codeVerifier, codeChallenge };
}

/**
 * Build the Keycloak authorization URL for an Authorization Code + PKCE S256 flow.
 *
 * @param {string}  codeChallenge  From generatePkceParams().codeChallenge
 * @param {string}  [state]        CSRF token; auto-generated if omitted.
 *                                 Persist in session; validate on callback.
 * @param {string}  [nonce]        Replay nonce; include when consuming id_token.
 * @returns {Promise<{ authUrl: string, state: string }>}
 */
async function buildAuthUrl(codeChallenge, state, nonce) {
  const client = await getPkceClient();
  const _state = state || generators.state();
  const params = {
    scope:                  'openid profile email',
    code_challenge:         codeChallenge,
    code_challenge_method:  'S256',
    state:                  _state,
  };
  if (nonce) params.nonce = nonce;
  const authUrl = client.authorizationUrl(params);
  return { authUrl, state: _state };
}

/**
 * Exchange an authorization code for tokens (PKCE S256 verification).
 *
 * Call this in the OAuth callback route handler.
 * The callbackUrl is the full incoming request URL (including query string).
 *
 * Returns a TokenSet containing at minimum:
 *   access_token   -- Bearer token for downstream API calls
 *   id_token       -- OIDC identity token (JWT; validate nonce if supplied)
 *   refresh_token  -- if realm is configured to issue refresh tokens
 *
 * @param {string} callbackUrl   Full URL of the callback request (with ?code=...&state=...)
 * @param {string} expectedState State value retrieved from user session
 * @param {string} codeVerifier  Code verifier retrieved from user session
 * @returns {Promise<import('openid-client').TokenSet>}
 * @throws  On state mismatch, PKCE failure, or Keycloak error response.
 */
async function exchangeCode(callbackUrl, expectedState, codeVerifier) {
  const client        = await getPkceClient();
  const redirectUri   = process.env.KC_SPA_REDIRECT_URI || 'http://localhost:3000/callback';
  const callbackParams = client.callbackParams(callbackUrl);
  return client.callback(
    redirectUri,
    callbackParams,
    { code_verifier: codeVerifier, state: expectedState }
  );
}

// ── Client Credentials (M2M, confidential client) ────────────────────────────

/**
 * Lazily build (and cache) the confidential M2M client for kh-node-svc.
 *
 * Keycloak client registration requirements:
 *   client_id          : kh-node-svc
 *   Access Type        : confidential
 *   Service Accounts   : enabled
 *   Standard Flow      : disabled
 *
 * KC_NODE_SVC_SECRET must be set to the client secret shown in Keycloak Admin UI
 * (Clients > kh-node-svc > Credentials tab).
 *
 * @returns {Promise<import('openid-client').Client>}
 */
async function getM2mClient() {
  if (_m2mClient) return _m2mClient;
  if (!process.env.KC_NODE_SVC_SECRET) {
    throw new Error(
      'KC_NODE_SVC_SECRET is not set. ' +
      'Obtain the client secret from Keycloak Admin UI: ' +
      `${KC_BASE_URL}/admin/master/console/#/${KC_REALM}/clients`
    );
  }
  const issuer = await discoverIssuer();
  _m2mClient = new issuer.Client({
    client_id:                  process.env.KC_NODE_SVC_CLIENT_ID || 'kh-node-svc',
    client_secret:              process.env.KC_NODE_SVC_SECRET,
    token_endpoint_auth_method: 'client_secret_basic',
  });
  return _m2mClient;
}

/**
 * Obtain an M2M access token via the Client Credentials grant.
 * Token is NOT cached here -- caller may cache with expiry if desired.
 * Typical access_token lifetime: 300 s (Keycloak realm default).
 *
 * @param {string} [scope]  Space-separated additional scopes (optional).
 * @returns {Promise<string>}  Raw access token string for use in Authorization headers.
 */
async function getM2mToken(scope) {
  const client  = await getM2mClient();
  const grantParams = { grant_type: 'client_credentials' };
  if (scope) grantParams.scope = scope;
  const tokenSet = await client.grant(grantParams);
  return tokenSet.access_token;
}

// ── Token introspection ───────────────────────────────────────────────────────

/**
 * Introspect an access token at the Keycloak introspection endpoint.
 * Uses the M2M confidential client as the introspecting party.
 *
 * Returns the RFC 7662 introspection response:
 *   { active: true,  sub, preferred_username, realm_access, ... }
 *   { active: false }   -- expired or revoked token
 *
 * Use this in API middleware to validate inbound Bearer tokens without
 * loading the full JWKS for local signature verification.
 *
 * @param {string} accessToken  Bearer token to introspect.
 * @returns {Promise<object>}   Introspection claims object.
 */
async function introspect(accessToken) {
  const client = await getM2mClient();
  return client.introspect(accessToken);
}

// ── Health probe ──────────────────────────────────────────────────────────────

/**
 * Lightweight connectivity probe: attempts OIDC discovery against Keycloak.
 * Returns true if Keycloak is reachable and discovery succeeds.
 * Does not throw; safe to call during startup health checks.
 *
 * @returns {Promise<boolean>}
 */
async function isKeycloakReachable() {
  try {
    // Reset cache so a previously failed discovery gets retried
    _issuer = null;
    await discoverIssuer();
    return true;
  } catch (_err) {
    return false;
  }
}

// ── Exports ───────────────────────────────────────────────────────────────────
module.exports = {
  // Issuer
  discoverIssuer,

  // PKCE (Authorization Code + PKCE S256)
  generatePkceParams,
  buildAuthUrl,
  exchangeCode,

  // M2M (Client Credentials)
  getM2mToken,

  // Introspection
  introspect,

  // Health
  isKeycloakReachable,

  // Config constants (useful for Express route/middleware setup)
  KC_BASE_URL,
  KC_REALM,
  DISCOVERY_URL,
};
