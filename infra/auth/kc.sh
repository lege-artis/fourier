#!/usr/bin/env bash
# kc.sh -- Keycloak realm administration helper (AUTH-002)
# Project: VibeCodeProjects / VibeCodeProjects
#
# COMMANDS
#   status           -- probe Keycloak health/ready endpoint
#   export           -- export vibedev realm to infra/auth/realm-export/
#   import           -- import vibedev realm from infra/auth/realm-export/
#   create-realm     -- create vibedev realm via Admin REST API (idempotent)
#   create-clients   -- register all required clients (idempotent; 409 = already exists)
#   bootstrap        -- create-realm + create-clients in one step
#
# ENVIRONMENT (defaults suit LDE; override for other envs)
#   KC_BASE_URL              http://localhost:8090
#   KC_REALM                 vibedev
#   KEYCLOAK_ADMIN           admin
#   KEYCLOAK_ADMIN_PASSWORD  admin_dev
#   KC_DB_PASSWORD           keycloak_dev  (used by compose; not needed here)
#
# USAGE
#   ./infra/auth/kc.sh status
#   ./infra/auth/kc.sh bootstrap
#   ./infra/auth/kc.sh export
#   ./infra/auth/kc.sh import
#
# NOTES
#   - Run from any directory; paths are resolved relative to this script.
#   - 'export' uses docker exec into the running keycloak container.
#   - 'create-clients' is idempotent: HTTP 409 (conflict) is treated as success.
#   - ASCII-only comments throughout (PS 5.1 compatibility for any caller).

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
KC_BASE="${KC_BASE_URL:-http://localhost:8090}"
KC_REALM="${KC_REALM:-vibedev}"
KC_ADMIN="${KEYCLOAK_ADMIN:-admin}"
KC_ADMIN_PWD="${KEYCLOAK_ADMIN_PASSWORD:-admin_dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_DIR="${SCRIPT_DIR}/realm-export"
CONTAINER="keycloak"

# ── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}  [OK]   $*${NC}"; }
fail() { echo -e "${RED}  [FAIL] $*${NC}" >&2; }
info() { echo -e "${YELLOW}  [INFO] $*${NC}"; }

# ── Admin token (master realm resource owner password grant) ──────────────────
kc_token() {
  local token
  token=$(curl -sf \
    -d "client_id=admin-cli" \
    -d "username=${KC_ADMIN}" \
    -d "password=${KC_ADMIN_PWD}" \
    -d "grant_type=password" \
    "${KC_BASE}/realms/master/protocol/openid-connect/token" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
  echo "${token}"
}

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_status() {
  # KC24: /health/ready is on the management port (9000, container-internal only).
  # Host-side probe uses /realms/master on the main port (KC_BASE = :8090).
  info "Probing ${KC_BASE}/realms/master ..."
  if curl -sf "${KC_BASE}/realms/master" | python3 -m json.tool; then
    ok "Keycloak is reachable (realm/master endpoint OK)."
  else
    fail "Keycloak probe failed -- is the container running? (docker ps --filter name=keycloak)"
    exit 1
  fi
}

cmd_export() {
  info "Exporting realm '${KC_REALM}' from container '${CONTAINER}' ..."
  mkdir -p "${EXPORT_DIR}"

  # Run Keycloak export tool inside the running container
  docker exec "${CONTAINER}" \
    /opt/keycloak/bin/kc.sh export \
      --realm "${KC_REALM}" \
      --dir   /tmp/realm-export \
      --users realm_file

  # Copy exported files to host
  docker cp "${CONTAINER}:/tmp/realm-export/." "${EXPORT_DIR}/"
  ok "Realm export written to: ${EXPORT_DIR}/"
  ls -lh "${EXPORT_DIR}/"
}

cmd_import() {
  IMPORT_FILE="${EXPORT_DIR}/${KC_REALM}-realm.json"
  if [[ ! -f "${IMPORT_FILE}" ]]; then
    fail "Import file not found: ${IMPORT_FILE}"
    info "Run: $0 export  first, or place ${KC_REALM}-realm.json in ${EXPORT_DIR}/"
    exit 1
  fi
  info "Importing realm '${KC_REALM}' into container '${CONTAINER}' ..."
  docker cp "${IMPORT_FILE}" "${CONTAINER}:/tmp/${KC_REALM}-realm.json"
  docker exec "${CONTAINER}" \
    /opt/keycloak/bin/kc.sh import \
      --file "/tmp/${KC_REALM}-realm.json"
  ok "Import complete."
}

cmd_create_realm() {
  info "Creating realm '${KC_REALM}' (idempotent) ..."
  TOKEN=$(kc_token)
  HTTP_STATUS=$(curl -so /dev/null -w "%{http_code}" \
    -X POST "${KC_BASE}/admin/realms" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"realm\":   \"${KC_REALM}\",
      \"enabled\": true,
      \"displayName\": \"VibeCodeProjects Dev\",
      \"sslRequired\": \"none\",
      \"registrationAllowed\": false,
      \"loginWithEmailAllowed\": true,
      \"duplicateEmailsAllowed\": false,
      \"accessTokenLifespan\": 300,
      \"refreshTokenMaxReuse\": 0
    }")
  if [[ "${HTTP_STATUS}" == "201" ]]; then
    ok "Realm '${KC_REALM}' created (201)."
  elif [[ "${HTTP_STATUS}" == "409" ]]; then
    ok "Realm '${KC_REALM}' already exists (409 -- skipped)."
  else
    fail "Realm creation failed -- HTTP ${HTTP_STATUS}"
    exit 1
  fi
}

cmd_create_clients() {
  info "Registering clients in realm '${KC_REALM}' ..."
  TOKEN=$(kc_token)
  REALM_URL="${KC_BASE}/admin/realms/${KC_REALM}"

  # Helper: POST a client JSON; 201 = created, 409 = already exists
  create_client() {
    local payload="$1"
    local client_id
    client_id=$(echo "${payload}" | python3 -c "import sys,json; print(json.load(sys.stdin)['clientId'])")
    info "  Registering: ${client_id}"
    local HTTP_STATUS
    HTTP_STATUS=$(curl -so /dev/null -w "%{http_code}" \
      -X POST "${REALM_URL}/clients" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "${payload}")
    if [[ "${HTTP_STATUS}" == "201" ]]; then
      ok "  ${client_id} created (201)."
    elif [[ "${HTTP_STATUS}" == "409" ]]; then
      ok "  ${client_id} already exists (409 -- skipped)."
    else
      fail "  ${client_id} -- HTTP ${HTTP_STATUS}"
    fi
  }

  # ── kh-sim-spa: public client, Authorization Code + PKCE S256 ────────────
  create_client '{
    "clientId": "kh-sim-spa",
    "name":     "KH-Sim SPA",
    "publicClient": true,
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "serviceAccountsEnabled": false,
    "attributes": {
      "pkce.code.challenge.method": "S256"
    },
    "redirectUris": [
      "http://localhost:3000/*",
      "http://localhost:3001/*"
    ],
    "webOrigins": [
      "http://localhost:3000",
      "http://localhost:3001"
    ]
  }'

  # ── kh-node-svc: confidential, client_credentials (M2M) ──────────────────
  create_client '{
    "clientId": "kh-node-svc",
    "name":     "KH-Sim Node.js Service",
    "publicClient": false,
    "serviceAccountsEnabled": true,
    "standardFlowEnabled": false,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false
  }'

  # ── kh-py-svc: confidential, client_credentials (M2M) ────────────────────
  create_client '{
    "clientId": "kh-py-svc",
    "name":     "KH-Sim Python Service",
    "publicClient": false,
    "serviceAccountsEnabled": true,
    "standardFlowEnabled": false,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false
  }'

  # ── gh-actions-oidc: token exchange receiver (AUTH-005 scope -- stub) ─────
  # Full IdP brokering setup (GitHub JWKS trust) done in AUTH-005.
  # Created here as a placeholder so realm export captures the client skeleton.
  create_client '{
    "clientId": "gh-actions-oidc",
    "name":     "GitHub Actions OIDC (stub -- AUTH-005)",
    "publicClient": false,
    "serviceAccountsEnabled": true,
    "standardFlowEnabled": false,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "attributes": {
      "use.refresh.tokens": "false"
    }
  }'

  ok "Client registration complete."
}

cmd_bootstrap() {
  info "Bootstrap: create-realm + create-clients"
  cmd_create_realm
  cmd_create_clients
  ok "Bootstrap complete. Recommend running: $0 export  to persist realm state."
}

usage() {
  echo ""
  echo "Usage: $0 <command>"
  echo ""
  echo "Commands:"
  echo "  status           Probe Keycloak health/ready endpoint"
  echo "  export           Export vibedev realm to infra/auth/realm-export/"
  echo "  import           Import vibedev realm from infra/auth/realm-export/"
  echo "  create-realm     Create vibedev realm via Admin REST API (idempotent)"
  echo "  create-clients   Register all required clients (idempotent)"
  echo "  bootstrap        create-realm + create-clients in one step"
  echo ""
  echo "Env overrides: KC_BASE_URL, KC_REALM, KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD"
  echo ""
}

# ── Dispatch ──────────────────────────────────────────────────────────────────
case "${1:-help}" in
  status)         cmd_status ;;
  export)         cmd_export ;;
  import)         cmd_import ;;
  create-realm)   cmd_create_realm ;;
  create-clients) cmd_create_clients ;;
  bootstrap)      cmd_bootstrap ;;
  help|--help|-h) usage ;;
  *) echo "Unknown command: ${1}. Run: $0 help" >&2; exit 1 ;;
esac
