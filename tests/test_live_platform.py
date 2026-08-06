import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.live_platform_client import LivePlatformClient

client = LivePlatformClient()

print("=" * 60)
print("SERVER HEALTH")
print("=" * 60)

print(client.server_health())

print()

print("=" * 60)
print("SERVICES")
print("=" * 60)

print(client.list_services())