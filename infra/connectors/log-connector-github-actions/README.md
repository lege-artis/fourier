# log-connector-github-actions

Composite GitHub Actions action that ships a CI job result document to
Elasticsearch (`test-results-{YYYY.MM.DD}` index) via `curl`.

Part of the VibeCodeProjects log-infra pipeline (LOG-004).

---

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `es_host` | yes | — | Elasticsearch base URL, e.g. `http://localhost:9200` |
| `suite` | yes | — | Test suite identifier, e.g. `rust-build-test` |
| `status` | yes | — | Job outcome: `pass` \| `fail` \| `skip` |
| `duration_ms` | no | `"0"` | Elapsed wall-clock time in milliseconds |

## Index / document schema

Index pattern: `test-results-YYYY.MM.DD` (date-partitioned, daily rollover).

```json
{
  "@timestamp":  "2026-04-03T14:22:01Z",
  "suite":       "rust-build-test",
  "status":      "pass",
  "duration_ms": 4823,
  "run_id":      "12345678901",
  "run_number":  42,
  "workflow":    "CI Heartbeat",
  "branch":      "main"
}
```

## Usage

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Record start time
        id: timer
        run: echo "start=$(date +%s%3N)" >> "$GITHUB_OUTPUT"

      - name: Run tests
        id: tests
        run: make test

      - name: Compute duration
        id: duration
        if: always()
        run: |
          END=$(date +%s%3N)
          echo "ms=$(( END - ${{ steps.timer.outputs.start }} ))" >> "$GITHUB_OUTPUT"

      - name: Ship result to Elasticsearch
        if: always()
        uses: ./infra/connectors/log-connector-github-actions
        with:
          es_host:     http://localhost:9200
          suite:       rust-build-test
          status:      ${{ job.status }}
          duration_ms: ${{ steps.duration.outputs.ms }}
```

## Behaviour

- **Non-fatal:** if `curl` returns a non-zero exit code (ES unreachable, index
  locked, network timeout) the step logs a warning and exits `0` — the calling
  job is never failed by this action.
- **No auth:** designed for the local-dev ELK stack (no TLS, no API key).
  For production use, extend `inputs` with `es_api_key` and pass
  `-H "Authorization: ApiKey ${INPUT}"` to the curl call.
- **Depends on:** LOG-001 (ELK stack healthy). No MongoDB dependency.

## Tested by

LOG-005 — `log-infra-test` job in `.github/workflows/ci-heartbeat.yml`.
