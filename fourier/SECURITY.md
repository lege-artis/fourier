# Security Policy

## Supported Versions

kh-sim is currently in early development (v0.1.0-scaffold). Only the latest
commit on the `thinkpad` branch receives security attention.

| Version       | Supported |
|---------------|-----------|
| 0.1.x (HEAD)  | yes       |
| earlier       | no        |

## Scope

kh-sim is a local-first numerical simulation benchmark. It is **not intended
for internet-facing deployment** in its current form. The HTTP backends listen
on localhost by default and carry no authentication layer.

Known intentional limitations (not treated as vulnerabilities):
- No authentication on `/simulate`, `/health`, `/info` endpoints
- Newman/Postman collections may include plaintext environment variable stubs
- MongoDB log service has no access control in dev configuration

## Reporting a Vulnerability

If you discover a security issue that would affect a user running kh-sim in a
networked or shared environment, please report it privately before opening a
public issue.

**Contact:** petr.yamyang@gmail.com  
**Subject line:** `[kh-sim SECURITY] <brief description>`

Expected response time: within 7 days. If the issue is confirmed, a fix or
mitigation note will be published in the next commit and credited to the reporter
(unless anonymity is requested).

Do not open a public GitHub issue for security-sensitive findings until a fix
or documented mitigation is in place.
