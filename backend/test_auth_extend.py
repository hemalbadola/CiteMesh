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

    # Register or ensure exists
    email = "twofa@example.com"
    pwd = "secret1234"
    r = requests.post(
        f"{BASE}/auth/register",
        json={"email": email, "password": pwd, "full_name": "Two Fa"},
        timeout=5,
    )
    assert r.status_code in (201, 400), r.text

    # Login once to confirm basic path works (2FA not yet enabled)
    r = requests.post(
        f"{BASE}/auth/login",
        data={"username": email, "password": pwd},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,
    )
    if r.status_code == 428:
        # Already has 2FA enabled; skip to 2FA login flow
        pass
    else:
        r.raise_for_status()

    # Get bearer for setup endpoints
    token = None
    if r.ok and r.headers.get("content-type", "").startswith("application/json"):
        token = r.json().get("access_token")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Setup 2FA and enable
    r = requests.post(f"{BASE}/auth/2fa/setup", headers=headers, timeout=5)
    r.raise_for_status()
    secret = r.json()["secret"]

    import pyotp

    code = pyotp.TOTP(secret).now()
    r = requests.post(f"{BASE}/auth/2fa/enable", headers=headers, params={"code": code}, timeout=5)
    r.raise_for_status()

    # Now normal login should demand 2FA
    r = requests.post(
        f"{BASE}/auth/login",
        data={"username": email, "password": pwd},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,
    )
    assert r.status_code == 428, r.text

    # Do 2FA login
    code = pyotp.TOTP(secret).now()
    r = requests.post(
        f"{BASE}/auth/login/2fa",
        params={"code": code},
        data={"username": email, "password": pwd},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,
    )
    r.raise_for_status()
    token2 = r.json()["access_token"]
    print("2FA login OK, token prefix:", token2[:12])


if __name__ == "__main__":
    run()
