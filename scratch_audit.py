import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("c:/Ganesh_149/Bhiv QCG works/master file/Insight_Constitutional_Runtime/.env")

url = "https://marine-quantum-runtime-final.onrender.com"
api_key = os.getenv("Quantum_Runtime_Auth_Key")
headers = {"X-API-Key": api_key}
print(f"API_KEY present: {bool(api_key)}")

def check(name, req_fn):
    print(f"\n--- {name} ---")
    try:
        r = req_fn()
        print(f"Status: {r.status_code}")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")

check("Health (no auth)", lambda: requests.get(f"{url}/health"))
check("Health Detailed (auth)", lambda: requests.get(f"{url}/health/detailed", headers=headers))
check("Health Detailed (wrong auth)", lambda: requests.get(f"{url}/health/detailed", headers={"X-API-Key": "wrong"}))
check("Capabilities", lambda: requests.get(f"{url}/api/v1/capabilities", headers=headers))
check("Providers", lambda: requests.get(f"{url}/api/v1/quantum/providers", headers=headers))

signal_payload = {
    "payload": {
        "confidence": 0.92,
        "energy_delta": 0.0001,
        "iterations": 120,
        "node_id": "qnode_01",
        "variance": 0.002,
    }
}
check("Signal Execute (valid)", lambda: requests.post(f"{url}/api/v1/capability/signal", json=signal_payload, headers=headers))

invalid_signal = {"payload": {"confidence": 0.92}}
check("Signal Execute (invalid)", lambda: requests.post(f"{url}/api/v1/capability/signal", json=invalid_signal, headers=headers))

pipeline_payload = {
    "payload": {
        "salinity": 35.2,
        "temperature_celsius": 18.5,
        "pH": 7.8,
        "material_oxidation_potential": 0.44,
        "dissolved_oxygen_mgl": 6.5,
        "current_density_mAcm2": 0.12,
    }
}
check("Pipeline Execute", lambda: requests.post(f"{url}/api/v1/capability/quantum_pipeline", json=pipeline_payload, headers=headers))

direct_q_payload = {
    "num_qubits": 2,
    "gate_sequence": [
        {"gate": "h", "qubits": [0]},
        {"gate": "cx", "qubits": [0, 1]},
    ],
    "shots": 1024,
    "preferred_provider": "local_simulator",
    "require_simulator": True,
}
check("Direct Quantum Execute", lambda: requests.post(f"{url}/api/v1/quantum/execute", json=direct_q_payload, headers=headers))
