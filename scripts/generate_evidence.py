import json
import os
from pathlib import Path

# Fix python path for imports
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.quantum_adapter import MarineQuantumAdapter

evidence_dir = PROJECT_ROOT / "evidence_packet"
evidence_dir.mkdir(parents=True, exist_ok=True)

adapter = MarineQuantumAdapter(mode="live", runtime_url="https://marine-quantum-runtime-final.onrender.com")

# 1. Health
health_res = adapter.health()
with open(evidence_dir / "ganesh_live_endpoint_health.json", "w") as f:
    json.dump(health_res, f, indent=4)

# 2. Capability
caps_res = adapter.list_capabilities()
with open(evidence_dir / "ganesh_live_capability_response.json", "w") as f:
    json.dump(caps_res, f, indent=4)

# 3. Execution (which should be blocked by 401)
payload = {
    "salinity": 35.2,
    "temperature_celsius": 18.5,
    "pH": 7.8,
    "material_oxidation_potential": 0.44,
    "dissolved_oxygen_mgl": 6.5,
    "current_density_mAcm2": 0.12,
}
exec_res = adapter.invoke_capability("quantum_pipeline", payload)
with open(evidence_dir / "ganesh_provider_failure.json", "w") as f:
    json.dump(exec_res, f, indent=4)

print("Evidence generation complete.")
