# KH-SIM — Pascal Backend

**Task:** KH-007 | **Framework:** fphttpapp (FPC) | **Port:** 8005

## Endpoint contract

Implements the shared OpenAPI spec: `kh-sim/shared/api/openapi.yaml`

| Endpoint | Method | Description |
|----------|--------|-------------|
| /simulate | POST | Run KH simulation step(s), return field snapshot |
| /health | GET | Backend health + DB connectivity |
| /info | GET | Language/framework/version metadata |

## Physics kernel

Imports `kh-sim/shared/physics/` — KH instability core adapted from `kh-instability-sim.zip`.
Do NOT duplicate physics logic in backend — call shared kernel via FFI / native import.

## Status

Blocked on KH-002 (extract kh-instability-sim.zip, adapt physics core).
