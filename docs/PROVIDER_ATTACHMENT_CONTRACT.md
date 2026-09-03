# Provider Attachment Contract

**Adapter:** `MarineQuantumAdapter`
**Location:** `src/platform/quantum_adapter.py`
**Supported Mode:** `QUANTUM_LOCAL` only (live mode returns `UNAVAILABLE`)

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `QUANTUM_RUNTIME_MODE` | Execution mode. Only `LOCAL` is currently supported. | `local` |
| `QUANTUM_RUNTIME_URL` | Base URL of the Marine Quantum Runtime HTTP API. | `http://localhost:8000` |
| `QUANTUM_RUNTIME_API_KEY` | API key sent as `X-API-Key` header. | `dev-insecure-key` |

---

## Required Provider Endpoints

A live provider attached to this adapter must expose the following HTTP endpoints.

### `GET /health`

Returns runtime health status.

**Expected response:**
```json
{
  "status": "HEALTHY",
  "heartbeat": "ALIVE"
}
```

The adapter wraps this and stamps `"mode": "LOCAL"` and `"heartbeat": {"heartbeat": "ALIVE"}` in its own health response.

---

### `GET /api/v1/capabilities`

Returns a list of registered capability descriptors.

**Expected response:**
```json
[
  {
    "capability_id": "quantum_pipeline",
    "authority_ceiling": "QUANTUM_EXECUTION",
    ...
  }
]
```

The adapter accepts `capability_id`, `id`, or `name` as the capability identifier field.

---

### `POST /api/v1/capability/{capability_id}`

Invokes a named capability.

**Request body:**
```json
{
  "payload": { ... }
}
```

**Expected success response:**
```json
{
  "status": "SUCCESS",
  "capability_id": "quantum_pipeline",
  "invocation_id": "<string>",
  "deterministic_hash": "<string>",
  "output": { ... }
}
```

**Expected validation failure response (HTTP 422):**
```json
{
  "errors": [ ... ]
}
```

---

## Adapter Behavior

| Condition | Adapter Response |
|---|---|
| Mode is not `LOCAL` | Returns `UNAVAILABLE` immediately, no HTTP call made |
| Provider unreachable (`ConnectionError`, `Timeout`) | Returns `FAILED` with error details |
| Provider returns HTTP 422 | Returns `VALIDATION_ERROR` with `errors` list |
| Successful invocation | Stamps `runtime_mode: LOCAL`, `quantum_provider_source: Marine Quantum Runtime`, `execution_classification: QUANTUM_LOCAL` |

---

## Classification Guarantee

The adapter **always** stamps the following on every result it returns:

```json
{
  "runtime_mode": "LOCAL",
  "quantum_provider_source": "Marine Quantum Runtime",
  "execution_classification": "QUANTUM_LOCAL"
}
```

A result without these fields did not pass through this adapter.

---

## What a Live Provider Must NOT Do

- Must not return `execution_classification: QUANTUM_LIVE` unless actual quantum hardware was used.
- Must not suppress error details on validation failure.
- Must not return a success status for an out-of-range input.
