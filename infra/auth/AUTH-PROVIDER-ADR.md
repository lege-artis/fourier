# AUTH-PROVIDER-ADR — OAuth2.0 Provider Evaluation
**Task:** AUTH-001  
**Status:** Accepted  
**Date:** 2026-04-11  
**Author:** ThinkPad / CoWork session 2026-04-11  
**Version:** 1.0.0

---

## Context

The VibeCodeProjects platform requires an OAuth2.0 / OpenID Connect (OIDC) authorization layer to serve four distinct integration surfaces:

| Surface | Task | Runtime | Notes |
|---|---|---|---|
| React F/E (kh-sim) SPA auth | AUTH-002/003 | Browser | PKCE mandatory — no client secret in browser |
| Node.js connector (kh-sim log-service, future microservices) | AUTH-002 | Node 20/LTS | openid-client, server-side token exchange |
| Python connector (log-connector-python, FastAPI/Flask services) | AUTH-003 | Python 3.11 | authlib, JWT validation, introspection endpoint |
| WordPress SSO (zemla.org / mim2000.cz / bodyterapie.com) | AUTH-004 | WordPress 6.x / PHP 8.x | Plugin-level OAuth2.0; MacBook-only task |
| GitHub Actions OIDC (keyless CI/CD token exchange) | AUTH-005 | GitHub Actions | No long-lived secrets; OIDC federated identity |

The provider choice gates AUTH-002 through AUTH-006. Self-hosted versus SaaS, grant type support, and cost model are the dominant discriminators given the project profile: open-source, self-hosted infrastructure stack, zero recurring SaaS budget for dev/test, WordPress on shared hosting.

---

## Decision Drivers

1. **Zero recurring cost at dev/test scale** — project runs on ThinkPad LDE + GitHub Actions free tier.
2. **Self-hosted alignment** — the existing stack is Docker Compose / local; no managed-cloud dependency preferred for core auth.
3. **PKCE support** — SPAs and CLI tools require Authorization Code + PKCE (RFC 7636); implicit flow is deprecated (RFC 9700).
4. **GitHub Actions OIDC federation** — AUTH-005 requires the provider to accept GitHub's OIDC JWT as a federated token (via `subject_token_type=urn:ietf:params:oauth2:token-type:jwt` or JWKS endpoint trust).
5. **WordPress plugin ecosystem** — AUTH-004 sites need a mature WordPress OAuth2.0 client plugin with configurable endpoints.
6. **Node.js + Python library support** — `openid-client` (Node) and `authlib` (Python) must have documented integration paths with the chosen provider.
7. **Docker image quality** — provider must have an official or widely-adopted container image compatible with the `infra/docker/` compose stack.

---

## Options Evaluated

### Option A — Keycloak (self-hosted)

**Description:** Red Hat–sponsored, enterprise-grade IAM. Runs as a standalone Java service. Provides full OIDC/OAuth2.0 server, admin UI, realm/client/role model.

**Container:** `quay.io/keycloak/keycloak:latest` (official). Keycloak 24+ uses Quarkus runtime, single-JAR, ~500 MB image.

**Grant types supported:** Authorization Code + PKCE, Client Credentials, Device Authorization, Refresh Token, Token Exchange (admin API), GitHub Actions OIDC federation via external IdP / identity brokering.

**PKCE:** Full support since Keycloak 7.x. Enforced per-client via `pkce.code.challenge.method=S256`.

**GitHub Actions OIDC federation:** Supported via Keycloak Identity Brokering — configure `github` as external OIDC IdP using GitHub's JWKS endpoint (`https://token.actions.githubusercontent.com/.well-known/jwks`). The Actions JWT `sub` (e.g. `repo:org/repo:ref:refs/heads/main`) maps to a Keycloak identity via mapper policy.

**WordPress:** Multiple mature plugins available — `miniOrange OAuth 2.0 Client` (free tier), `WP OAuth Server` (client-side), `KeyCloak SSO` dedicated plugin. Standard OIDC discovery endpoint (`/realms/{realm}/.well-known/openid-configuration`) enables generic plugin configuration.

**Node.js + Python:** `openid-client` has first-class Keycloak examples. `authlib` supports generic OIDC, tested against Keycloak. Both require standard OIDC discovery URL — no provider-specific SDK needed.

**Cost:** Free / open-source (Apache 2.0). Docker image self-hosted; no per-seat fee.

**Resource footprint:** ~512 MB RAM minimum in dev mode; ~1 GB recommended for production. PostgreSQL (or H2 for dev) as backend. Requires dedicated port (default 8080 — conflicts with Nginx :8080 in LDE; must remap to e.g. :8090 or :18080).

**Complexity:** High initial configuration (realm setup, client registration, IdP brokering for GitHub). Admin UI mitigates this. Long-term, most operationally complete option.

---

### Option B — Auth0 (SaaS, free tier)

**Description:** Okta-owned SaaS IAM. Free tier: 7,500 monthly active users, unlimited logins, 2 social connections.

**Grant types:** Authorization Code + PKCE, Client Credentials, Device Flow, Refresh Token. GitHub social connection built-in.

**PKCE:** Full support.

**GitHub Actions OIDC federation:** Not directly supported on free tier. Auth0 requires an Action (paid feature) or custom code to validate an inbound GitHub OIDC JWT. Keyless CI/CD (AUTH-005) is non-trivial on free tier.

**WordPress:** `Auth0 Login for WordPress` official plugin. Good documentation.

**Node.js + Python:** Official Auth0 SDKs available; also works with `openid-client` / `authlib` via standard discovery.

**Cost:** Free tier adequate for dev/test. Production scale requires paid plan ($23+/month). Introduces SaaS dependency — token validation requires internet connectivity; breaks airgapped LDE.

**LDE integration:** Discovery endpoint is `https://{tenant}.auth0.com/.well-known/openid-configuration` — external HTTPS; integration tests inside Docker network require internet egress. Inconsistent with local-first LDE architecture.

**Verdict:** SaaS dependency and GitHub Actions OIDC gap on free tier disqualify Auth0 for this stack. Local-first LDE + AUTH-005 requirements cannot be met without paid plan.

---

### Option C — GitHub OAuth (GitHub.com as IdP)

**Description:** Use GitHub.com's OAuth2.0 application (`https://github.com/login/oauth/authorize`) as the sole provider, scoped to GitHub identity.

**Grant types:** Authorization Code only (no PKCE enforcement; `code_challenge` parameter is ignored by GitHub OAuth apps). Device Flow supported for CLI.

**PKCE:** Not enforced by GitHub OAuth apps. GitHub OAuth does not issue OIDC `id_token` — it returns a GitHub access token, not a JWT. Standard OIDC `userinfo` endpoint available at `https://api.github.com/user`.

**GitHub Actions OIDC federation:** GitHub Actions emits OIDC JWTs signed by `https://token.actions.githubusercontent.com`. A GitHub OAuth app cannot act as an OIDC token exchange server — it is a client of GitHub, not a provider. AUTH-005 requires an OIDC-capable server to accept the GitHub-issued JWT; GitHub OAuth app itself cannot fulfill this role.

**WordPress:** `GitHub OAuth` plugins exist (e.g. `WP GitHub OAuth`) but lack PKCE and full OIDC flows. Authorization Code without PKCE is insufficient for SPA auth in modern WordPress setups.

**Node.js + Python:** Works with `openid-client` in OAuth mode (no PKCE). `authlib` can use GitHub as OAuth2.0 backend. No JWT `id_token` means custom identity resolution via `/user` API call.

**Cost:** Free.

**Verdict:** GitHub OAuth covers simple "login with GitHub" use cases but cannot serve as a general OIDC provider. AUTH-005 keyless CI/CD requires a server that consumes GitHub's OIDC token, not one that is itself a GitHub OAuth client. PKCE enforcement gap is a security concern for SPAs. Insufficient scope for this ADR.

---

### Option D — PKCE-only (no dedicated IdP, each service implements PKCE inline)

**Description:** Each microservice independently implements Authorization Code + PKCE against GitHub OAuth or another social provider. No centralized token server.

**Analysis:** This is not a provider option but an architectural anti-pattern for multi-service platforms. Token validation logic duplicated across Node.js, Python, WordPress, and CI tooling violates DRY and creates inconsistent security posture. No central revocation, no role model, no token introspection endpoint. Eliminated early.

---

## Decision

**Chosen: Option A — Keycloak (self-hosted)**

Keycloak is the only option that satisfies all five integration surfaces — SPA PKCE, Node.js/Python connectors, WordPress SSO, and GitHub Actions OIDC federation — without a SaaS dependency or internet-egress requirement during LDE runs.

The key discriminator for AUTH-005 is GitHub Actions OIDC federation: Keycloak's Identity Brokering feature can be configured to trust GitHub's JWKS endpoint (`https://token.actions.githubusercontent.com`) as an external IdP, allowing a GitHub Actions workflow to exchange its `ACTIONS_ID_TOKEN_REQUEST_TOKEN` for a Keycloak access token via the token-exchange grant. Auth0 requires a paid plan for this; GitHub OAuth cannot be the receiving party; PKCE-only has no server-side component.

Port conflict resolution: Keycloak default port :8080 conflicts with Nginx. Keycloak will be mapped to host port **:8090** in the LDE compose stack. OIDC discovery URL (internal): `http://localhost:8090/realms/vibedev/.well-known/openid-configuration`.

---

## Architecture Sketch

```
┌──────────────────────────────────────────────────────────────────────┐
│  LDE stack (docker-compose.r0-lde.yml)                               │
│                                                                      │
│  ┌─────────────────┐   OIDC discovery    ┌──────────────────────┐   │
│  │ kh-sim React SPA│ ◄──────────────────► │ Keycloak :8090       │   │
│  │ (browser PKCE)  │   /realms/vibedev   │ realm: vibedev        │   │
│  └─────────────────┘                    │ client: kh-sim-spa    │   │
│                                          │ client: kh-node-svc   │   │
│  ┌─────────────────┐   client_creds      │ client: kh-py-svc     │   │
│  │ kh-log-service  │ ──────────────────► │ client: gh-actions    │   │
│  │ Node.js :8006   │   Bearer JWT        │                       │   │
│  └─────────────────┘                    │  IdP broker:          │   │
│                                          │  github-actions-oidc  │   │
│  ┌─────────────────┐   authlib OIDC      │  (JWKS trust)         │   │
│  │ Python connector│ ──────────────────► └──────────────────────┘   │
│  │ log-connector   │                            ▲                    │
│  └─────────────────┘                            │ OIDC JWT           │
│                                                  │ (token exchange)  │
│  ┌─────────────────┐                    ┌────────┴─────────────┐    │
│  │ GitHub Actions  │ ──────────────────► │ GitHub OIDC          │    │
│  │ AUTH-005        │   federated token   │ token.actions.github │    │
│  └─────────────────┘   exchange          └──────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘

WordPress sites (external, shared hosting)
  zemla.org / mim2000.cz / bodyterapie.com
  → WordPress OAuth2.0 client plugin → Keycloak :8090 (or cloud-hosted
    Keycloak instance for production WordPress SSO — AUTH-004 scope)
```

---

## Keycloak LDE Integration Specification

### Docker Compose service stub (to be implemented in AUTH-002)

```yaml
  keycloak:
    image: quay.io/keycloak/keycloak:24.0
    command: start-dev
    environment:
      KEYCLOAK_ADMIN:          admin
      KEYCLOAK_ADMIN_PASSWORD: "${KC_ADMIN_PASSWORD}"
      KC_DB:                   dev-file        # embedded H2, dev-only
      KC_HTTP_PORT:            8090
    ports:
      - "8090:8090"
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:8090/health/ready || exit 1"]
      interval: 15s
      timeout: 10s
      retries: 8
      start_period: 30s
```

**Note:** `start-dev` mode uses embedded H2 (ephemeral). Production Keycloak requires PostgreSQL; a `keycloak-db` compose service (postgres:15-alpine) to be added in AUTH-002 PR.

### Realm / Client configuration (AUTH-002 scope)

| Item | Value |
|---|---|
| Realm | `vibedev` |
| SPA client ID | `kh-sim-spa` |
| SPA grant types | Authorization Code + PKCE (S256); `publicClient: true` |
| Node client ID | `kh-node-svc` |
| Node grant types | Client Credentials; `confidentialClient: true` |
| Python client ID | `kh-py-svc` |
| Python grant types | Client Credentials; `confidentialClient: true` |
| GitHub Actions client | `gh-actions-oidc` |
| GitHub Actions grant | Token Exchange; IdP broker `github-actions`; JWKS: `https://token.actions.githubusercontent.com` |

### Port allocation addition (CLAUDE.md convention)

```
keycloak :8090  (AUTH-002; dev mode, vibedev realm)
```

---

## Consequences

**Positive:**
- Single OIDC provider for all integration surfaces — consistent JWT validation across Node.js, Python, WordPress.
- No internet dependency during LDE integration tests.
- GitHub Actions OIDC federation via token exchange eliminates long-lived CI secrets.
- Keycloak admin UI provides observable realm/client/session state during AUTH-002 development.
- `openid-client` and `authlib` both support standard OIDC discovery — no provider-specific SDK lock-in.

**Negative / Risks:**
- Keycloak `start-dev` (H2 backend) is ephemeral — state is lost on container restart. Acceptable for dev; AUTH-002 PR must document the realm import/export workflow (`kc.sh export --dir /opt/keycloak/data/import`).
- JVM startup time: Keycloak 24 Quarkus adds ~15–30 s to `Start-LocalEnv.ps1 -Action up` cold-start. Health poll backoff in `Check-SessionEnv.ps1` should be increased to `start_period: 30s` + 8 retries.
- WordPress SSO (AUTH-004) on shared hosting cannot reach `http://localhost:8090` — requires a cloud-reachable Keycloak instance or tunneling (e.g. ngrok). AUTH-004 scope will document this constraint. Production path: Keycloak on a VPS or Keycloak-as-a-Service (RHBK cloud free tier).
- Port :8090 added to LDE stack — must not conflict with existing allocation. Confirmed: no current service uses :8090.

---

## Implementation Order (post-ADR)

```
AUTH-001  [DONE]  This ADR
AUTH-002  [open]  Keycloak compose service + realm config + Node.js openid-client PKCE module
AUTH-003  [open]  Python authlib OIDC integration (depends AUTH-001)
AUTH-005  [open]  GitHub Actions OIDC token exchange (depends GEN-010; JWKS trust in Keycloak)
AUTH-004  [open]  WordPress SSO plugin — MacBook; cloud Keycloak instance scoping (depends AUTH-001)
AUTH-006  [open]  Smoke tests: token flow e2e per connector (depends AUTH-002, 003, 005)
```

---

## References

- RFC 6749 — The OAuth 2.0 Authorization Framework
- RFC 7636 — Proof Key for Code Exchange by OAuth Public Clients (PKCE)
- RFC 8693 — OAuth 2.0 Token Exchange
- RFC 9700 — Best Current Practice for OAuth 2.0 Security (deprecates implicit flow)
- Keycloak 24 Documentation: https://www.keycloak.org/documentation
- GitHub Actions OIDC: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- `openid-client` Node.js: https://github.com/panva/node-openid-client
- `authlib` Python: https://docs.authlib.org/en/latest/
