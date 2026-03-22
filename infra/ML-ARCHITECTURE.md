# ML Stack Architecture — TensorFlow MLOps
**Project:** VibeCodeProjects — TensorFlow Integration
**Version:** 1.0.0 | **Date:** 2026-03-22
**Status:** Design complete — implementation pending

---

## Architecture Pattern: ML Microservice + Model Registry

Full training + inference stack. TensorFlow Serving runs as an isolated Docker
microservice. All application languages access it through standardised REST or
gRPC connectors. Models are versioned in a local registry (Git LFS for
repo-tracked models, filesystem for large artifacts).

```
┌───────────────────────────────────────────────────────────────────────┐
│  TRAINING PIPELINE                                                    │
│                                                                       │
│  Python (TF 2.x) ──► SavedModel ──► /ml/models/{name}/{version}/     │
│  ml/training/pipeline.py            (Model Registry — Git LFS)        │
│  ml/validation/validate_model.py                                       │
└───────────────────────┬───────────────────────────────────────────────┘
                        │ mount
┌───────────────────────▼───────────────────────────────────────────────┐
│  TF SERVING (Docker)                                                  │
│                                                                       │
│  REST  port 8501:  POST /v1/models/{model}/versions/{ver}:predict     │
│  gRPC  port 8500:  PredictionService.Predict (protobuf)               │
└─────┬────────────────────────┬──────────────────────────┬─────────────┘
      │ REST                   │ gRPC                     │ REST
┌─────▼──────┐      ┌──────────▼────────┐      ┌─────────▼──────────┐
│ Node.js    │      │ Scala / JVM       │      │ Rust               │
│ fetch/     │      │ gRPC + protobuf   │      │ reqwest (REST)     │
│ axios      │      │ stubs             │      │ tonic  (gRPC)      │
└────────────┘      └───────────────────┘      └────────────────────┘
```

---

## Component Inventory

| Component | Technology | Port | Docker |
|-----------|-----------|------|--------|
| Training pipeline | Python 3.11 + TensorFlow 2.x | — | No (local) |
| Model registry | Filesystem + Git LFS | — | No |
| TF Serving | tensorflow/serving:latest | 8500 (gRPC), 8501 (REST) | Yes |
| tf-connector-node | Node.js + fetch | — | No |
| tf-connector-scala-grpc | Scala + gRPC protobuf | — | No |
| tf-connector-rust-rest | Rust + reqwest | — | No |
| tf-connector-rust-grpc | Rust + tonic | — | No |

---

## Model Registry Layout

```
ml/
├── models/                        ← Git LFS tracked
│   ├── {model_name}/
│   │   ├── 1/                     ← version 1 (SavedModel format)
│   │   │   ├── saved_model.pb
│   │   │   └── variables/
│   │   └── 2/                     ← version 2
│   │       ├── saved_model.pb
│   │       └── variables/
│   └── MODEL-REGISTRY.md          ← version manifest
├── training/
│   ├── pipeline.py                ← training entry point
│   ├── requirements.txt           ← TF + deps
│   └── configs/                   ← model hyperparameter configs
└── validation/
    ├── validate_model.py          ← accuracy + latency thresholds
    └── test_inputs/               ← canonical test tensors
```

---

## TF Serving Docker Compose

**File:** `infra/docker/tensorflow-serving/docker-compose.yml`

```yaml
version: "3.8"

services:
  tf-serving:
    image: tensorflow/serving:latest
    container_name: vibe-tf-serving
    ports:
      - "8500:8500"   # gRPC
      - "8501:8501"   # REST
    volumes:
      - ../../../ml/models:/models:ro
    environment:
      - MODEL_BASE_PATH=/models
      - MODEL_NAME=default
    command: >
      --model_config_file=/models/models.config
      --model_config_file_poll_wait_seconds=60
      --allow_version_labels_for_unavailable_models=true
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8501/v1/models/default || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Optional: TF Serving with GPU
  # tf-serving-gpu:
  #   image: tensorflow/serving:latest-gpu
  #   runtime: nvidia
  #   ...
```

**Model config file** (`ml/models/models.config`):
```protobuf
model_config_list {
  config {
    name: "default"
    base_path: "/models/default"
    model_platform: "tensorflow"
    model_version_policy {
      latest { num_versions: 2 }
    }
  }
}
```

---

## REST API Contract

**Base URL:** `http://localhost:8501`

### Predict (latest version)
```
POST /v1/models/{model_name}:predict
Content-Type: application/json

{
  "instances": [
    {"input_tensor": [[1.0, 2.0, 3.0]]}
  ]
}
```

### Predict (specific version)
```
POST /v1/models/{model_name}/versions/{version}:predict
```

### Model status
```
GET /v1/models/{model_name}
GET /v1/models/{model_name}/versions/{version}
```

### Response format
```json
{
  "predictions": [[0.1, 0.7, 0.2]],
  "model_spec": {
    "name": "default",
    "version": "1",
    "signature_name": "serving_default"
  }
}
```

---

## gRPC API Contract

**Endpoint:** `localhost:8500`
**Proto:** `tensorflow_serving/apis/prediction_service.proto`

```protobuf
service PredictionService {
  rpc Predict (PredictRequest) returns (PredictResponse);
  rpc GetModelStatus (GetModelStatusRequest) returns (GetModelStatusResponse);
}
```

Generated stubs location:
- Scala: `infra/connectors/tf-connector/scala-grpc/src/main/protobuf/`
- Rust: `infra/connectors/tf-connector/rust-grpc/proto/`

---

## Connector Implementation Targets

See `infra/connectors/TF-CONNECTOR-SPEC.md` for full API contracts.

### tf-connector-node (REST)
```javascript
// infra/connectors/tf-connector/node-rest/index.js
const TFClient = require('./tf-client');
const client = new TFClient({ host: 'localhost', port: 8501 });
const result = await client.predict('default', { instances: [...] });
```

### tf-connector-scala-grpc
```scala
// infra/connectors/tf-connector/scala-grpc/src/main/scala/TFClient.scala
import tensorflow.serving.prediction_service.PredictionServiceGrpc
val channel = ManagedChannelBuilder.forAddress("localhost", 8500).usePlaintext().build()
val stub = PredictionServiceGrpc.stub(channel)
val response = stub.predict(request)
```

### tf-connector-rust-rest
```rust
// infra/connectors/tf-connector/rust-rest/src/lib.rs
pub async fn predict(model: &str, payload: Value) -> Result<Value, Error> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("http://localhost:8501/v1/models/{}:predict", model))
        .json(&payload)
        .send().await?;
    Ok(resp.json().await?)
}
```

### tf-connector-rust-grpc
```rust
// infra/connectors/tf-connector/rust-grpc/src/lib.rs
// Uses tonic + prost for protobuf
pub mod tensorflow_serving {
    tonic::include_proto!("tensorflow.serving");
}
```

---

## CI/CD Integration

Two new jobs added to `ci-heartbeat.yml`:

### ml-train-validate
```yaml
ml-train-validate:
  name: ML Training Pipeline Validation
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: '3.11' }
    - run: pip install -r ml/training/requirements.txt
    - run: python ml/training/pipeline.py --mode=smoke-test
    - run: python ml/validation/validate_model.py --threshold=0.80
    - name: Archive model artifact
      uses: actions/upload-artifact@v4
      with:
        name: trained-model-${{ github.run_number }}
        path: ml/models/
```

### ml-serve-test
```yaml
ml-serve-test:
  name: TF Serving Connector Tests
  runs-on: ubuntu-latest
  needs: [ml-train-validate]
  steps:
    - uses: actions/checkout@v4
    - name: Start TF Serving
      run: docker compose -f infra/docker/tensorflow-serving/docker-compose.yml up -d
    - name: Wait for serving ready
      run: timeout 60 bash -c 'until curl -sf http://localhost:8501/v1/models/default; do sleep 2; done'
    - name: Node.js connector test
      run: cd infra/connectors/tf-connector/node-rest && npm test
    - name: Rust REST connector test
      run: cd infra/connectors/tf-connector/rust-rest && cargo test
    - name: Scala gRPC connector test
      run: cd infra/connectors/tf-connector/scala-grpc && sbt test
```

---

## GitHub Repository Structure Impact

```
VibeCodeProjects/
├── infra/
│   ├── LOG-ARCHITECTURE.md          ← this doc's sibling
│   ├── ML-ARCHITECTURE.md           ← this doc
│   ├── docker/
│   │   ├── elasticsearch/
│   │   │   ├── docker-compose.yml
│   │   │   └── fluent-bit.conf
│   │   └── tensorflow-serving/
│   │       ├── docker-compose.yml
│   │       └── models.config        ← TF Serving model config
│   └── connectors/
│       ├── LOG-CONNECTOR-SPEC.md
│       ├── TF-CONNECTOR-SPEC.md
│       ├── log-connector-node/
│       ├── log-connector-python/
│       ├── log-connector-github-actions/
│       └── tf-connector/
│           ├── node-rest/
│           ├── scala-grpc/
│           ├── rust-rest/
│           └── rust-grpc/
├── ml/
│   ├── models/                      ← Git LFS
│   ├── training/
│   └── validation/
└── .github/workflows/
    └── ci-heartbeat.yml             ← +2 new jobs
```

---

## Resource Requirements (Local Dev)

| Component | RAM | Disk | GPU |
|-----------|-----|------|-----|
| TF Serving (Docker) | 1–2 GB | ~500 MB image | Optional |
| Training pipeline | 2–4 GB | model artifacts (Git LFS) | Recommended |
| **Total** | **3–6 GB peak** | **~1 GB + models** | — |

> Training with GPU: install CUDA 12.x + cuDNN 8.x, use `tensorflow/serving:latest-gpu`
> ThinkPad without discrete GPU: CPU training only — use small models / smoke-test datasets for CI

---

## Production Docker Image Template

TF Serving Compose is designed for direct promotion to production:
- Add `--enable_batching=true` for throughput optimization
- Add TLS termination via nginx reverse proxy
- Mount model registry from S3/GCS for cloud deployments
- Add Prometheus metrics endpoint (`--monitoring_config_file`)
