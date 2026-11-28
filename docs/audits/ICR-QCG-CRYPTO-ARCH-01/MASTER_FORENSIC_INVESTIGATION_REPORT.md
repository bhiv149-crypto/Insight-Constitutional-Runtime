# MASTER FORENSIC INVESTIGATION REPORT
## ICR–QCG Cryptographic Service Authentication & Ecosystem Trust Analysis

**Document ID:** ICR-QCG-CRYPTO-ARCH-01-DOC-01  
**Task ID:** ICR-QCG-CRYPTO-ARCH-01  
**Date:** 2026-11-27  
**Author:** Senior Technical Architect & Distributed Systems Auditor (Ganesh Vishwakarma Workspace)  
**Primary Repository:** `Insight-Constitutional-Runtime`  
**Classification:** SOURCE-CONFIRMED & TEST-VERIFIED  

---

## 1. Executive Summary

This forensic investigation was initiated to discover the exact architectural and cryptographic root causes behind the integration failure between the **Insight Constitutional Runtime (ICR)** and the **BHIV Quantum Computing Gateway (QCG)** ecosystem.

Previous troubleshooting reports hypothesized a simple "missing header" or "token mismatch." Our line-by-line static analysis and dynamic execution tracing reveal a profound **architectural mismatch** between two divergent security philosophies:
1. **ICR (Server-Side / Gateway):** Implemented an RFC-7519 / RFC-6750 Bearer authentication model (`HTTPBearer`) requiring a pre-shared static secret (`INSIGHT_EXECUTION_TOKEN`) or a signed HS256 JWT issued by InsightCore (`aud="insight-bridge"`).
2. **QCG Tantra Platform SDK (Client-Side):** Implemented an asymmetric request-signing scheme (`X-Service-*`) using NIST SECP256R1 (ECDSA P-256) via an abstract `TrustProvider` hierarchy, passing hex-encoded signatures and public keys without Bearer tokens.

When QCG SDK invoked ICR's canonical execution gateway (`POST /api/v1/execute`), FastAPI's `security = HTTPBearer()` dependency halted request execution at ingress, throwing **HTTP 403 Forbidden** before any cryptographic signature could be parsed or verified.

Furthermore, forensic analysis of QCG's signing protocol revealed **critical cryptographic vulnerabilities** (e.g., self-asserted public-key injection without server-side validation, absence of replay prevention, and unbound HTTP verbs) that would have created catastrophic security vulnerabilities had ICR simply accepted the presented public key without a trusted registry.

---

## 2. Repository Inventory and Baseline Identity

All four ecosystem repositories located in `C:\blackhole159_SV\Ganesh_temp` were forensically baselined:

| Repository Name | Local Absolute Path | Current Branch | Commit Hash | Working Tree Status | Role in Investigation |
|:---|:---|:---:|:---:|:---|:---|
| **Insight-Constitutional-Runtime (ICR)** | `C:\blackhole159_SV\Ganesh_temp\ICR\Insight-Constitutional-Runtime` | `feature/insight-icr-option-b-integration` | `5642d57` | Authorized Implementation Scope | Execution gateway & constitutional governance |
| **bhiv-QCG** | `C:\blackhole159_SV\Ganesh_temp\Team-side\bhiv-QCG` | `main` | `23a065d` | External / Read-Only | Tantra Platform SDK, provider adapters, telemetry |
| **Marine_Quantum_runtime-final** | `C:\blackhole159_SV\Ganesh_temp\Team-side\Marine_Quantum_runtime-final` | `main` | `2804974` | External / Read-Only | Quantum execution runtime & circuit backend |
| **BHIV_Quantum_Application_Layer (QAL)** | `C:\blackhole159_SV\Ganesh_temp\QAL\BHIV_Quantum_Application_Layer` | `main` | `085ec16` | External / Read-Only | Problem compilation & high-level quantum algorithms |

---

## 3. QCG Client-Side Signing Architecture

Forensic inspection was conducted on `Team-side/bhiv-QCG/platform_capability_sdk.py`, `Team-side/bhiv-QCG/sdk_auth.py`, and `Team-side/bhiv-QCG/quantum_trust_provider.py`.

### 3.1 HTTP POST Transmission Path
In [`platform_capability_sdk.py`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/bhiv-QCG/platform_capability_sdk.py#L708-L731):
```python
# Lines 708-727
def _http_post(self, url: str, data: dict) -> dict:
    payload = json.dumps(data, default=str).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-SDK-Version", "1.0.0")
    req.add_header("X-Trust-Level", self._trust_provider.trust_level())

    # Add auth headers
    auth_headers = self._authenticator.build_auth_headers(data)
    for key, value in auth_headers.items():
        req.add_header(key, value)
    ...
```
`_http_post` delegates header generation strictly to `self._authenticator.build_auth_headers(data)`.

### 3.2 Header Generation Implementation
In [`sdk_auth.py`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/bhiv-QCG/sdk_auth.py#L62-L87):
```python
# Lines 62-87
def build_auth_headers(self, request_payload: dict) -> Dict[str, str]:
    if not self._keypair:
        self.initialise()

    payload_bytes = json.dumps(request_payload, sort_keys=True, default=str).encode()
    signature = self._provider.sign(payload_bytes, self._keypair.private_key_handle)

    return {
        "X-Service-ID": self.service_id,
        "X-Service-Signature": signature.hex(),
        "X-Service-PublicKey": self._keypair.public_key.hex(),
        "X-Trust-Level": self._provider.trust_level(),
    }
```
**Key Observations [SOURCE-CONFIRMED]:**
1. **Headers Produced:**
   - `X-Service-ID`: Caller service identifier (e.g., `"tantra.platform.sdk"`).
   - `X-Service-Signature`: Hexadecimal string of the raw signature bytes.
   - `X-Service-PublicKey`: Hexadecimal string of the public key DER bytes.
   - `X-Trust-Level`: Trust level string (`"CLASSICAL"`, `"POST_QUANTUM"`, `"HYBRID"`).
2. **Data Signed:**
   - Evaluated as: `payload_bytes = json.dumps(request_payload, sort_keys=True, default=str).encode()`
   - Note: Uses standard Python `json.dumps()` where default separators are `(', ', ': ')` with spaces.
   - Note: Only the payload dictionary is signed. HTTP method (`POST`), URL path (`/api/v1/execute`), query parameters, and timestamp are NOT signed.

### 3.3 Cryptographic Provider Implementation
In [`quantum_trust_provider.py`](file:///C:/blackhole159_SV/Ganesh_temp/Team-side/bhiv-QCG/quantum_trust_provider.py#L125-L165):
```python
class ClassicalTrustProvider(TrustProvider):
    def trust_level(self) -> str:
        return TRUST_CLASSICAL

    def generate_key_pair(self) -> KeyPairResult:
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return KeyPairResult(
            public_key=public_key_bytes,
            private_key_handle=private_key,
            algorithm="ECDSA-P256",
            trust_level=TRUST_CLASSICAL,
        )

    def sign(self, data: bytes, key_handle: Any) -> bytes:
        return key_handle.sign(data, ec.ECDSA(hashes.SHA256()))

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        pub = serialization.load_der_public_key(public_key)
        pub.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
```
**Cryptographic Specs [SOURCE-CONFIRMED]:**
- Curve: NIST P-256 (`SECP256R1`).
- Hash: SHA-256 (`hashes.SHA256()`).
- Public Key Format: ASN.1 DER `SubjectPublicKeyInfo` (91 bytes).
- Signature Format: ASN.1 DER ECDSA signature (70–72 bytes).

---

## 4. ICR Server-Side Ingress Architecture

Forensic inspection was conducted on `ICR/Insight-Constitutional-Runtime/insight_execution_service.py` and `ICR/Insight-Constitutional-Runtime/src/common/jwt_security.py`.

### 4.1 Ingress Dependency Enforcement
In [`insight_execution_service.py`](file:///C:/blackhole159_SV/Ganesh_temp/ICR/Insight-Constitutional-Runtime/insight_execution_service.py#L75):
```python
# Line 75 (Original)
security = HTTPBearer()

# Lines 260-280 (Original)
def verify_execution_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    expected = (
        os.environ.get("INSIGHT_EXECUTION_TOKEN")
        or os.environ.get("INSIGHT_AUTH_TOKEN")
        or os.environ.get("INSIGHT_ENFORCE_TOKEN")
    )
    if not expected or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication token"
        )
    return token

@app.post("/api/v1/execute")
async def execute(
    req: InvocationRequest,
    token: str = Depends(verify_execution_token),
):
```
**Failure Mechanics [TEST-VERIFIED]:**
1. FastAPI's `HTTPBearer(auto_error=True)` intercepts incoming HTTP requests before `verify_execution_token` body executes.
2. If `Authorization: Bearer <token>` is absent, FastAPI automatically responds with:
   `HTTP/1.1 403 Forbidden`  
   `{"detail": "Not authenticated"}`
3. The Tantra SDK attaches solely `X-Service-*` headers and never sets `Authorization: Bearer ...`.
4. Therefore, every request from QCG SDK was rejected unconditionally at the web framework boundary.

---

## 5. Forensic Vulnerability Analysis of QCG Signing Contract

Our audit identified **four critical vulnerabilities** in QCG's existing signing protocol that must be remedied at the architectural level:

### Vulnerability 1: Self-Asserted Public-Key Injection (Identity Spoofing)
- **Mechanism:** In `SDKAuthenticator.build_auth_headers()`, the client generates an ephemeral keypair on the fly (`self.initialise()`) and transmits `X-Service-PublicKey: <hex>`.
- **Attack Vector:** An adversary can generate their own keypair, claim `X-Service-ID: insightflow.runtime.intelligence.v1`, sign an arbitrary malicious payload with their private key, and attach their public key in `X-Service-PublicKey`.
- **Severity:** **CRITICAL**. If the server validates the signature against the transmitted header key rather than a trusted registry, the adversary can forge any service identity in the ecosystem.

### Vulnerability 2: Absence of Replay Protection (Replay Attacks)
- **Mechanism:** The signed payload contains only `{"service_id", "operation", "payload", "version", "invocation_id"}`. No timestamp, expiration time (`exp`), or TTL window is enforced.
- **Attack Vector:** An eavesdropper on the network can record a legitimate signed request and replay it millions of times against ICR.
- **Severity:** **HIGH**. Results in unauthorized state execution, duplicate resource allocation, and denial of service.

### Vulnerability 3: Request Context Unbound (Cross-Endpoint Signature Confusion)
- **Mechanism:** The cryptographic signature covers only the serialized payload dictionary. It does not sign the HTTP Method (`POST`), URL Path (`/api/v1/execute`), or target host.
- **Attack Vector:** A signature generated for a benign capability query can be intercepted and submitted to a sensitive administrative or execution route.
- **Severity:** **MEDIUM**.

### Vulnerability 4: Privilege Escalation via Trust-Level Conflation
- **Mechanism:** QCG sends `X-Trust-Level: POST_QUANTUM` or `QUANTUM`.
- **Architectural Risk:** Confusing authentication ("who signed this?") with authorization ("what are they allowed to execute?"). An unprivileged client must not gain write access simply by signing with a post-quantum algorithm.
- **Severity:** **HIGH**.

---

## 6. Audit Verdict

| Finding ID | Classification | Location | Root Cause |
|:---|:---:|:---|:---|
| **FINDING-01** | **SOURCE-CONFIRMED** | `insight_execution_service.py:75` | `HTTPBearer()` hard blocks any request lacking `Authorization: Bearer ...`. |
| **FINDING-02** | **SOURCE-CONFIRMED** | `platform_capability_sdk.py:718` | Tantra SDK only transmits `X-Service-*` asymmetric signature headers. |
| **FINDING-03** | **TEST-VERIFIED** | `sdk_auth.py:65` | `build_auth_headers()` transmits unauthenticated self-asserted public key. |
| **FINDING-04** | **TEST-VERIFIED** | `sdk_auth.py:68` | Signing payload lacks timestamp and server-enforced replay cache. |
| **FINDING-05** | **SOURCE-CONFIRMED** | `quantum_trust_provider.py:170` | Post-quantum implementation in QCG is simulated HMAC, not real lattice math. |
