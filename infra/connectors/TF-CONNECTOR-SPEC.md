# TensorFlow Connector Specification
**Version:** 1.0.0 | **Date:** 2026-03-22
**TF Serving:** REST port 8501 | gRPC port 8500

---

## Request/Response Contract

### REST Predict Request
```
POST http://localhost:8501/v1/models/{model_name}:predict
POST http://localhost:8501/v1/models/{model_name}/versions/{version}:predict
Content-Type: application/json
```

```json
{
  "instances": [
    [1.0, 2.0, 3.0]
  ]
}
```

### REST Predict Response
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

### REST Model Status
```
GET http://localhost:8501/v1/models/{model_name}
```
```json
{
  "model_version_status": [{
    "version": "1",
    "state": "AVAILABLE",
    "status": { "error_code": "OK" }
  }]
}
```

---

## Connector A — tf-connector-node (REST)

**Path:** `infra/connectors/tf-connector/node-rest/`
**Language:** Node.js (ESM)
**Dependencies:** none (uses native fetch, Node 18+)

### Installation
```bash
# No dependencies — uses Node.js built-in fetch
```

### Usage
```javascript
import TFClient from './tf-connector-node/index.js';

const tf = new TFClient({
  host: 'localhost',
  port: 8501,
  model: 'default',
  version: null,          // null = latest
  timeoutMs: 5000
});

const result = await tf.predict([[1.0, 2.0, 3.0]]);
// result.predictions => [[0.1, 0.7, 0.2]]

const status = await tf.status();
// status.model_version_status[0].state => "AVAILABLE"
```

### Implementation
```javascript
// infra/connectors/tf-connector/node-rest/index.js
export default class TFClient {
  constructor({ host = 'localhost', port = 8501, model = 'default', version = null, timeoutMs = 5000 } = {}) {
    this.base = `http://${host}:${port}/v1/models/${model}`;
    this.versionPath = version ? `/versions/${version}` : '';
    this.timeoutMs = timeoutMs;
  }

  async predict(instances) {
    const url = `${this.base}${this.versionPath}:predict`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instances }),
      signal: AbortSignal.timeout(this.timeoutMs)
    });
    if (!res.ok) throw new Error(`TF Serving error: ${res.status} ${await res.text()}`);
    return res.json();
  }

  async status() {
    const res = await fetch(this.base, { signal: AbortSignal.timeout(this.timeoutMs) });
    if (!res.ok) throw new Error(`TF status error: ${res.status}`);
    return res.json();
  }
}
```

### Test
```javascript
// infra/connectors/tf-connector/node-rest/test.js
import TFClient from './index.js';
import assert from 'node:assert/strict';

const tf = new TFClient({ model: 'default' });
const status = await tf.status();
assert.equal(status.model_version_status[0].state, 'AVAILABLE', 'Model must be AVAILABLE');
console.log('tf-connector-node: PASS');
```

---

## Connector B — tf-connector-scala-grpc

**Path:** `infra/connectors/tf-connector/scala-grpc/`
**Language:** Scala 2.13 / 3.x
**Dependencies:** `grpc-netty`, `scalapb`, `tensorflow-serving-api`

### build.sbt
```scala
libraryDependencies ++= Seq(
  "io.grpc"              % "grpc-netty"          % "1.62.2",
  "com.thesamet.scalapb" %% "scalapb-runtime-grpc" % scalapb.compiler.Version.scalapbVersion,
  "io.grpc"              % "grpc-stub"           % "1.62.2"
)

// Generate stubs from .proto files in src/main/protobuf/
Compile / PB.targets := Seq(
  scalapb.gen() -> (Compile / sourceManaged).value / "scalapb"
)
```

### Usage
```scala
import io.grpc.ManagedChannelBuilder
import tensorflow.serving.prediction_service.PredictionServiceGrpc
import tensorflow.serving.predict.PredictRequest
import org.tensorflow.framework.tensor.TensorProto

object TFClient {
  def buildChannel(host: String = "localhost", port: Int = 8500) =
    ManagedChannelBuilder.forAddress(host, port).usePlaintext().build()

  def predict(modelName: String, input: TensorProto, version: Option[Long] = None)
             (implicit channel: io.grpc.ManagedChannel): TensorProto = {
    val stub = PredictionServiceGrpc.blockingStub(channel)
    val spec  = tensorflow.serving.model.ModelSpec.defaultInstance
      .withName(modelName)
      .withVersion(version.map(com.google.protobuf.wrappers.Int64Value.of).getOrElse(
        com.google.protobuf.wrappers.Int64Value.defaultInstance))
    val req   = PredictRequest.defaultInstance.withModelSpec(spec)
      .addInputs("input_tensor" -> input)
    stub.predict(req).outputsOrEmpty("output_0")
  }
}
```

### Proto files location
```
infra/connectors/tf-connector/scala-grpc/src/main/protobuf/
├── tensorflow/core/framework/tensor.proto
├── tensorflow_serving/apis/predict.proto
├── tensorflow_serving/apis/prediction_service.proto
└── tensorflow_serving/config/model_server_config.proto
```
> Copy from `tensorflow/serving` GitHub repo or use `tensorflow-serving-api` Maven artifact.

---

## Connector C — tf-connector-rust-rest

**Path:** `infra/connectors/tf-connector/rust-rest/`
**Language:** Rust (async, tokio)
**Dependencies:** `reqwest`, `serde`, `serde_json`, `tokio`

### Cargo.toml
```toml
[package]
name = "tf-connector-rust-rest"
version = "0.1.0"
edition = "2021"

[dependencies]
reqwest = { version = "0.12", features = ["json"] }
serde   = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio   = { version = "1.0", features = ["full"] }
```

### Implementation
```rust
// infra/connectors/tf-connector/rust-rest/src/lib.rs
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Serialize)]
pub struct PredictRequest {
    pub instances: Vec<Value>,
}

#[derive(Debug, Deserialize)]
pub struct PredictResponse {
    pub predictions: Vec<Value>,
}

pub struct TFClient {
    client: Client,
    base_url: String,
}

impl TFClient {
    pub fn new(host: &str, port: u16, model: &str) -> Self {
        Self {
            client: Client::new(),
            base_url: format!("http://{}:{}/v1/models/{}", host, port, model),
        }
    }

    pub async fn predict(&self, instances: Vec<Value>) -> Result<PredictResponse, reqwest::Error> {
        let req = PredictRequest { instances };
        self.client
            .post(format!("{}:predict", self.base_url))
            .json(&req)
            .send().await?
            .json::<PredictResponse>().await
    }

    pub async fn status(&self) -> Result<Value, reqwest::Error> {
        self.client.get(&self.base_url).send().await?.json().await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[tokio::test]
    async fn test_status() {
        let client = TFClient::new("localhost", 8501, "default");
        let status = client.status().await.expect("TF status call failed");
        assert!(status["model_version_status"][0]["state"].as_str() == Some("AVAILABLE"));
    }
}
```

---

## Connector D — tf-connector-rust-grpc

**Path:** `infra/connectors/tf-connector/rust-grpc/`
**Language:** Rust (async, tokio, tonic)
**Dependencies:** `tonic`, `prost`, `tokio`, `tonic-build`

### Cargo.toml
```toml
[package]
name = "tf-connector-rust-grpc"
version = "0.1.0"
edition = "2021"

[dependencies]
tonic    = "0.11"
prost    = "0.12"
tokio    = { version = "1.0", features = ["full"] }

[build-dependencies]
tonic-build = "0.11"
```

### build.rs
```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::configure()
        .build_client(true)
        .compile(
            &["proto/tensorflow_serving/apis/prediction_service.proto"],
            &["proto/"],
        )?;
    Ok(())
}
```

### Usage
```rust
// infra/connectors/tf-connector/rust-grpc/src/main.rs
use tonic::transport::Channel;
pub mod tensorflow_serving {
    tonic::include_proto!("tensorflow.serving");
}
use tensorflow_serving::prediction_service_client::PredictionServiceClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let channel = Channel::from_static("http://localhost:8500").connect().await?;
    let mut client = PredictionServiceClient::new(channel);
    // Build PredictRequest with TensorProto inputs...
    Ok(())
}
```

---

## Health Check Script (all connectors)

```bash
#!/bin/bash
# infra/connectors/tf-connector/health-check.sh
TF_HOST="${TF_HOST:-localhost}"
TF_REST_PORT="${TF_REST_PORT:-8501}"
MODEL="${TF_MODEL:-default}"

STATUS=$(curl -sf "http://${TF_HOST}:${TF_REST_PORT}/v1/models/${MODEL}" | \
  python3 -c "import sys,json; s=json.load(sys.stdin); \
  print(s['model_version_status'][0]['state'])")

if [ "$STATUS" = "AVAILABLE" ]; then
  echo "TF Serving HEALTHY: model=${MODEL} state=AVAILABLE"
  exit 0
else
  echo "TF Serving UNHEALTHY: model=${MODEL} state=${STATUS}"
  exit 1
fi
```

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `TF_SERVING_HOST` | TF Serving hostname | `localhost` |
| `TF_SERVING_REST_PORT` | REST API port | `8501` |
| `TF_SERVING_GRPC_PORT` | gRPC port | `8500` |
| `TF_MODEL_NAME` | Default model name | `default` |
| `TF_MODEL_VERSION` | Pinned version (null = latest) | `null` |
| `TF_TIMEOUT_MS` | Request timeout | `5000` |
