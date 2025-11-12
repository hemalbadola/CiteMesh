import time
import requests


BASE = "http://127.0.0.1:8001"


def wait_for_server(timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.ok:
                return True
        except Exception:
            time.sleep(0.3)
    return False


def run():
    assert wait_for_server(), "Server not responding on /health"

    # Register user (idempotent attempt)
    email = "demo@example.com"
    pwd = "secret1234"
    r = requests.post(
        f"{BASE}/auth/register",
        json={"email": email, "password": pwd, "full_name": "Demo User"},
        timeout=5,
    )
    assert r.status_code in (201, 400), r.text

    # Login
    r = requests.post(
        f"{BASE}/auth/login",
        data={"username": email, "password": pwd},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,
    )
    r.raise_for_status()
    token = r.json()["access_token"]

    # Me
    r = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    r.raise_for_status()
    data = r.json()
    assert data["email"] == email
    print("Smoke OK:", data)


if __name__ == "__main__":
    run()
