import subprocess
import time
import requests
import sys

def run_test():
    # Start the server in a subprocess to simulate production startup
    print("Starting production server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "insight_execution_service:app", "--host", "0.0.0.0", "--port", "8008"],
        env={"PORT": "8008", "INSIGHT_SERVICE_URL": "http://127.0.0.1:8008"}
    )
    
    time.sleep(3) # Wait for startup
    
    try:
        # Test 1: Health
        print("Testing /api/v1/health...")
        resp = requests.get("http://127.0.0.1:8008/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "UP"
        print("PASS")
        
        # Test 2: Execution Route (Flow)
        print("Testing /api/v1/execute (InsightFlow)...")
        req = {
            "service_id": "insightflow.runtime.intelligence.v1",
            "operation": "execute",
            "payload": {"test": True},
            "version": "1.0.0",
            "invocation_id": "prod-test-1"
        }
        resp = requests.post("http://127.0.0.1:8008/api/v1/execute", json=req)
        assert resp.status_code == 200
        assert resp.json()["status"] == "SUCCESS"
        print("PASS")
        
        # Test 3: Unknown service
        print("Testing Unknown Service...")
        req["service_id"] = "unknown"
        resp = requests.post("http://127.0.0.1:8008/api/v1/execute", json=req)
        assert resp.status_code == 404
        assert resp.json()["status"] == "NOT_FOUND"
        print("PASS")
        
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    run_test()
