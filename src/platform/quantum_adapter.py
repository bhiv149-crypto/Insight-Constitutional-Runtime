"""
Marine Quantum Runtime Adapter

Thin, reversible adapter over the local Marine Quantum Runtime.

Purpose:
    Provide an isolated gateway for InsightBridge to discover, query, and
    invoke local Quantum capabilities without modifying the canonical
    PlatformSDKAdapter, without embedding Marine internal source code, and
    without altering the existing BHIV/QCG integration.

Hard Boundaries:
    - Does NOT alter PlatformSDKAdapter or LivePlatformClient.
    - Does NOT replace QCG or establish a parallel global registry.
    - Fails closed (with clear error structures) if Marine is unreachable.
"""

from __future__ import annotations

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("insight.platform.quantum_adapter")

DEFAULT_MARINE_RUNTIME_PATH = r"C:\Ganesh_149\Marine-quantum-runtime\marine_quantum_runtime_capability_platform\marine_quantum_runtime"


class MarineQuantumAdapter:
    """
    Isolated adapter to interface with the local Marine Quantum Runtime.
    """

    def __init__(
        self,
        mode: Optional[str] = None,
        runtime_path: Optional[str] = None,
    ) -> None:
        self.mode = (mode or os.getenv("QUANTUM_RUNTIME_MODE", "local")).lower()
        self.runtime_path = runtime_path or os.getenv(
            "QUANTUM_RUNTIME_PATH", DEFAULT_MARINE_RUNTIME_PATH
        )

    def _check_ready(self) -> Optional[Dict[str, Any]]:
        """
        Check if the runtime environment is ready.
        Returns None if ready, or an error dictionary if unavailable.
        """
        if self.mode != "local":
            return {
                "status": "UNAVAILABLE",
                "mode": self.mode,
                "error": f"Unsupported QUANTUM_RUNTIME_MODE '{self.mode}' (expected 'local')",
                "runtime_path": self.runtime_path,
            }

        runtime_dir = Path(self.runtime_path)
        if not runtime_dir.exists():
            return {
                "status": "UNAVAILABLE",
                "mode": self.mode,
                "error": f"Marine Quantum Runtime path does not exist: {self.runtime_path}",
                "runtime_path": self.runtime_path,
            }

        return None

    def _run_marine_script(self, script: str, args: List[str] = None) -> tuple[int, str, str]:
        """
        Execute a python snippet in the Marine runtime directory in an isolated process.
        """
        cmd = [sys.executable, "-c", script]
        if args:
            cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                cwd=self.runtime_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return proc.returncode, proc.stdout, proc.stderr
        except Exception as exc:
            return 1, "", str(exc)

    def health(self) -> Dict[str, Any]:
        """
        Query health and heartbeat from the local Marine Quantum Runtime.
        """
        err_resp = self._check_ready()
        if err_resp:
            return err_resp

        script = (
            "import json\n"
            "from src.runtime import runtime_observability\n"
            "h = runtime_observability.get_runtime_health()\n"
            "hb = runtime_observability.get_runtime_heartbeat()\n"
            "print(json.dumps({'health': h, 'heartbeat': hb}))\n"
        )
        code, stdout, stderr = self._run_marine_script(script)
        if code != 0:
            return {
                "status": "ERROR",
                "mode": "LOCAL",
                "error": stderr.strip() or "Process exited with non-zero code",
                "runtime_path": self.runtime_path,
            }

        try:
            data = json.loads(stdout.strip().splitlines()[-1])
            hb = data.get("heartbeat", {})
            return {
                "status": "HEALTHY" if hb.get("heartbeat") == "ALIVE" else "DEGRADED",
                "mode": "LOCAL",
                "heartbeat": hb,
                "health": data.get("health", {}),
                "runtime_path": self.runtime_path,
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "mode": "LOCAL",
                "error": f"Failed to parse health response: {exc}",
                "raw_output": stdout,
                "runtime_path": self.runtime_path,
            }

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """
        List all registered quantum and runtime capabilities from Marine.
        """
        if self._check_ready():
            return []

        script = (
            "import json\n"
            "from src.runtime import runtime_capability_registry\n"
            "caps = runtime_capability_registry.list_capabilities()\n"
            "print(json.dumps(caps))\n"
        )
        code, stdout, stderr = self._run_marine_script(script)
        if code != 0:
            logger.error("Marine list_capabilities failed: %s", stderr)
            return []

        try:
            return json.loads(stdout.strip().splitlines()[-1])
        except Exception as exc:
            logger.error("Failed to parse capabilities list: %s", exc)
            return []

    def discover_capability(self, capability_id: str) -> Optional[Dict[str, Any]]:
        """
        Discover a specific capability descriptor from Marine.
        """
        if self._check_ready():
            return None

        script = (
            "import json, sys\n"
            "from src.runtime import runtime_capability_registry\n"
            "try:\n"
            "    desc = runtime_capability_registry.discover_capability(sys.argv[1])\n"
            "    print(json.dumps(desc.to_dict()))\n"
            "except Exception as e:\n"
            "    print(json.dumps({'error': str(e)}))\n"
        )
        code, stdout, stderr = self._run_marine_script(script, [capability_id])
        if code != 0:
            logger.warning("Marine discover_capability failed: %s", stderr)
            return None

        try:
            data = json.loads(stdout.strip().splitlines()[-1])
            if "error" in data:
                return None
            return data
        except Exception as exc:
            logger.warning("Failed to parse capability descriptor: %s", exc)
            return None

    def invoke_capability(self, capability_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a capability on the local Marine Quantum Runtime through its full pipeline.
        """
        err_resp = self._check_ready()
        if err_resp:
            return err_resp

        script = (
            "import json, sys\n"
            "from src.runtime import capability_runtime\n"
            "cap_id = sys.argv[1]\n"
            "payload = json.loads(sys.argv[2])\n"
            "res = capability_runtime.invoke_capability(cap_id, payload)\n"
            "print(json.dumps(res))\n"
        )
        code, stdout, stderr = self._run_marine_script(
            script, [capability_id, json.dumps(payload)]
        )
        if code != 0:
            logger.error("Execution process error for '%s': %s", capability_id, stderr)
            return {
                "status": "FAILED",
                "capability_id": capability_id,
                "error": stderr.strip() or "Process exited with non-zero code",
                "runtime_mode": "LOCAL",
            }

        try:
            result = json.loads(stdout.strip().splitlines()[-1])
            if isinstance(result, dict):
                result["runtime_mode"] = "LOCAL"
                result["quantum_provider_source"] = "Marine Quantum Runtime"
            return result
        except Exception as exc:
            logger.error("Failed to parse invocation result for '%s': %s", capability_id, exc)
            return {
                "status": "FAILED",
                "capability_id": capability_id,
                "error": f"Failed to parse result: {exc}",
                "raw_output": stdout,
                "runtime_mode": "LOCAL",
            }
