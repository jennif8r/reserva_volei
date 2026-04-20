import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("EVOLUTION_API_URL")
key = os.getenv("EVOLUTION_API_KEY")
instance = os.getenv("EVOLUTION_API_INSTANCE")

headers = {"apikey": key}

print(f"--- Diagnóstico Evolution API ---")
print(f"URL: {url}")
print(f"Instance: {instance}")

try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Root status: {r.status_code}")
except Exception as e:
    print(f"Erro no Root: {e}")

try:
    r = requests.get(f"{url}/instance/fetchInstances", headers=headers, timeout=10)
    print(f"Fetch Instances status: {r.status_code}")
    if r.status_code == 200:
        print(f"Instâncias: {r.text[:200]}...")
except Exception as e:
    print(f"Erro no Fetch Instances: {e}")

try:
    r = requests.get(f"{url}/instance/connectionState/{instance}", headers=headers, timeout=10)
    print(f"Connection State status: {r.status_code}")
    print(f"Resposta: {r.text}")
except Exception as e:
    print(f"Erro no Connection State: {e}")
