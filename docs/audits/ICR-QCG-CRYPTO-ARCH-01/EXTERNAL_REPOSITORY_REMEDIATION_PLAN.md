# EXTERNAL REPOSITORY REMEDIATION SPECIFICATIONS
## Exact Implementation Instructions for External Ecosystem Owners

**Document ID:** ICR-QCG-CRYPTO-ARCH-01-DOC-06  
**Task ID:** ICR-QCG-CRYPTO-ARCH-01  
**Date:** 2026-11-27  
**Author:** Senior Technical Architect & Independent Technical Auditor  
**Primary Repository:** `Insight-Constitutional-Runtime`  
**Execution Authority:** STRICT READ-ONLY ON EXTERNAL REPOSITORIES — SPECIFICATIONS ONLY  

---

## 1. Governance and Ownership Statement

In strict adherence to the ownership boundaries defined in Section 4 of the Master Engineering Prompt, **no files in external repositories were edited, committed, or modified**.

The specifications below provide exact, copy-paste ready implementation designs, file paths, line references, code patches, and verification criteria for the respective repository owners:

---

## 2. Remediation Spec 1: Tantra Platform SDK / QCG

**Target Repository:** `Team-side/bhiv-QCG`  
**Responsible Owners:** Pritesh Patra (Platform Lead) & Kanishk Singh (SDK Architect)  
**Priority:** P0 (Integration & Security Hardening)  

### 2.1 File: `sdk_auth.py`
**Affected Class:** `SDKAuthenticator`  
**Location:** [`Team-side/bhiv-QCG/sdk_auth.py:62-87`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/bhiv-QCG/sdk_auth.py#L62-L87)  

#### Problem & Root Cause:
1. `build_auth_headers()` transmits self-asserted `X-Service-PublicKey` without attaching a key identifier (`X-Service-KeyID`) or timestamp (`X-Service-Timestamp`).
2. Does not support optional Bearer token authorization header, preventing access to Bearer-only legacy endpoints.

#### Recommended Code Remediation:
```python
# In sdk_auth.py — Enhanced SDKAuthenticator
import time
from datetime import datetime, timezone

class SDKAuthenticator:
    def __init__(
        self,
        service_id: str,
        trust_provider: TrustProvider = None,
        bearer_token: Optional[str] = None,
        key_id: str = "default",
    ):
        self.service_id = service_id
        self._provider = trust_provider or ClassicalTrustProvider()
        self._keypair: Optional[KeyPairResult] = None
        self.bearer_token = bearer_token or os.getenv("BHIV_RUNTIME_AUTH_TOKEN")
        self.key_id = key_id

    def build_auth_headers(self, request_payload: dict) -> Dict[str, str]:
        if not self._keypair:
            self.initialise()

        now_iso = datetime.now(timezone.utc).isoformat()
        payload_bytes = json.dumps(request_payload, sort_keys=True, default=str).encode()
        signature = self._provider.sign(payload_bytes, self._keypair.private_key_handle)

        headers = {
            "X-Service-ID": self.service_id,
            "X-Service-KeyID": self.key_id,
            "X-Service-Timestamp": now_iso,
            "X-Service-Signature": signature.hex(),
            "X-Service-PublicKey": self._keypair.public_key.hex(),
            "X-Trust-Level": self._provider.trust_level(),
        }

        # Attach Bearer token if configured for dual-mode ingress compatibility
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        return headers
```

### 2.2 File: `quantum_trust_provider.py`
**Affected Class:** `PostQuantumTrustProvider`  
**Location:** [`Team-side/bhiv-QCG/quantum_trust_provider.py:165-225`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/bhiv-QCG/quantum_trust_provider.py#L165-L225)  

#### Problem & Root Cause:
`PostQuantumTrustProvider` uses `_SimulatedDilithium` which simulates signatures using 32-byte HMAC-SHA256, providing zero real quantum security.

#### Recommended Code Remediation:
Upgrade to native `cryptography.hazmat.primitives.asymmetric.mldsa` (NIST FIPS 204):
```python
# In quantum_trust_provider.py
from cryptography.hazmat.primitives.asymmetric import mldsa

class PostQuantumTrustProvider(TrustProvider):
    """Production-grade NIST FIPS 204 ML-DSA Post-Quantum Trust Provider."""

    def __init__(self, parameter_set: str = "ML-DSA-44"):
        self.parameter_set = parameter_set
        self._keypair: Optional[mldsa.MLDSA44PrivateKey] = None

    def trust_level(self) -> str:
        return TRUST_POST_QUANTUM

    def generate_key_pair(self) -> KeyPairResult:
        private_key = mldsa.MLDSA44PrivateKey.generate()
        public_key = private_key.public_key()
        pub_bytes = public_key.public_bytes_raw()
        return KeyPairResult(
            public_key=pub_bytes,
            private_key_handle=private_key,
            algorithm="ML-DSA-44",
            trust_level=TRUST_POST_QUANTUM,
        )

    def sign(self, data: bytes, key_handle: Any) -> bytes:
        return key_handle.sign(data)

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        try:
            pub = mldsa.MLDSA44PublicKey.from_public_bytes(public_key)
            pub.verify(signature, data)
            return True
        except Exception:
            return False
```

### 2.3 File: `web_server.py`
**Affected Module:** QCG Telemetry Server  
**Location:** [`Team-side/bhiv-QCG/web_server.py:302-335`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/bhiv-QCG/web_server.py#L302-L335)  

#### Problem & Root Cause:
QCG lacks telemetry ingestion route handlers for `POST /telemetry/execution`, `POST /telemetry/contract_lineage`, and `POST /telemetry/adapter_trace`, causing ICR's `LiveTraceStore` to fail with HTTP 404.

#### Recommended Code Remediation:
Add the missing ingestion endpoints to `web_server.py`:
```python
@app.post("/telemetry/execution")
async def ingest_execution_telemetry(payload: dict):
    trace_id = payload.get("trace_id") or str(uuid.uuid4())
    logger.info(f"Ingested execution trace {trace_id}")
    return {"status": "RECORDED", "trace_id": trace_id}

@app.post("/telemetry/contract_lineage")
async def ingest_contract_lineage(payload: dict):
    return {"status": "RECORDED", "lineage_id": payload.get("invocation_id")}

@app.post("/telemetry/adapter_trace")
async def ingest_adapter_trace(payload: dict):
    return {"status": "RECORDED", "trace_id": payload.get("trace_id")}
```

---

## 3. Remediation Spec 2: Marine Quantum Runtime (MQR)

**Target Repository:** `Team-side/Marine_Quantum_runtime-final`  
**Responsible Owner:** Dhiraj Chavan (Quantum Runtime Lead)  
**Priority:** P1 (Routing Contract Clarification)  

### 3.1 File: `api_server.py`
**Location:** [`Team-side/Marine_Quantum_runtime-final/api_server.py:740, 1315`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/Marine_Quantum_runtime-final/api_server.py#L740)  

#### Problem & Root Cause:
Generic quantum circuits sent by QAL or ICR to `POST /api/v1/quantum/pipeline` fail with HTTP 422 because that route strictly validates 6 marine corrosion parameters (`salinity`, `temperature_celsius`, `pH`, `material_oxidation_potential`, `dissolved_oxygen_mgl`, `current_density_mAcm2`). MQR *already implements* generic circuit execution on `POST /api/v1/quantum/execute`, but lacks clear OpenAPI documentation and enum descriptions distinguishing the two routes.

#### Recommended Remediation:
1. Update OpenAPI tags and docstrings in `api_server.py`:
   - `@app.post("/api/v1/quantum/execute", tags=["Generic Quantum Execution"])`
   - `@app.post("/api/v1/quantum/pipeline", tags=["Specialized Marine Corrosion Pipeline"])`
2. Add a `/health` endpoint capability flag:
   `{"capabilities": {"generic_circuit_execution": true, "marine_pipeline": true, "hardware_qpu": false, "aer_simulator": true}}`.

---

## 4. Remediation Spec 3: Quantum Application Layer (QAL)

**Target Repository:** `QAL/BHIV_Quantum_Application_Layer`  
**Responsible Owner:** QAL Engineering Team  
**Priority:** P1 (Blocker Status Correction)  

### 4.1 File: `src/bhiv_quantum/api/service.py`
**Location:** [`QAL/BHIV_Quantum_Application_Layer/src/bhiv_quantum/api/service.py:680-688`](file:///C:/blackhole159_SV/Ganesh_temp/QAL/BHIV_Quantum_Application_Layer/src/bhiv_quantum/api/service.py#L680-L688)  

#### Problem & Root Cause:
Code claims `MQR-01: BLOCKED - Marine Quantum Runtime (MQR) lacks generic quantum execution endpoint`. This is factually incorrect. MQR line 740 implements `POST /api/v1/quantum/execute`. QAL failed because it passed invalid capability string `"generic_quantum_execution"` and lacked bearer token configuration.

#### Recommended Remediation:
1. Update status from `MQR-01: BLOCKED` to `MQR-01: OPERATIONAL`.
2. Configure QAL client runtime adapter to dispatch generic QAOA circuits to ICR using `quantum_capability: "quantum_circuit_execution"` and set `BHIV_RUNTIME_AUTH_TOKEN`.

---

## 5. Remediation Spec 4: VM Infrastructure Host 163.128.209.18

**Target Host:** Staging VM `163.128.209.18`  
**Responsible Owner:** Vijay (DevOps / Infrastructure Lead)  
**Priority:** P0 (Production Parity)  

#### Problem & Root Cause:
Port 8031 on the host runs an obsolete single-process script (`InsightFlow - Telemetry Ingestion`) exposing only `POST /telemetry/ingest`. Canonical ICR Option B (IWO :8031, ICRG :8029, IIE :8030) was never deployed; `/health` returns HTTP 404.

#### Recommended Remediation:
1. Stop legacy process on port 8031:
   `sudo systemctl stop insightflow-legacy`
2. Deploy Canonical Option B stack via Docker Compose:
   ```bash
   cd /opt/insight-constitutional-runtime
   docker compose -f docker-compose.yml up -d --build
   ```
3. Verify all three microservices respond on their respective ports:
   - `curl http://163.128.209.18:8031/health` (IWO)
   - `curl http://163.128.209.18:8029/health` (ICRG)
   - `curl http://163.128.209.18:8030/health` (IIE)
