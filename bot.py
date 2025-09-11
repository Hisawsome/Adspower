import os
import time
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# -------------------- SETTINGS --------------------
API_URL = "https://api.adspower.net/v1"
THREADS = 5  # how many accounts to run at once
PASSWORD = "RIDI"  # must be typed in full caps
# --------------------------------------------------

# Path for storing last checkin timestamp
LAST_CHECKIN_FILE = "last_checkin.txt"


def password_gate():
    """Require user to type RIDI before bot starts."""
    attempt = input("Enter password to start bot: ").strip()
    if attempt != PASSWORD:
        print("❌ Wrong password. Exiting.")
        exit()
    print("✅ Access granted. Bot starting...\n")


def load_accounts():
    """Load accounts from accounts.txt (JSON lines format)."""
    if not os.path.exists("accounts.txt"):
        print("⚠️ accounts.txt not found.")
        return []

    accounts = []
    with open("accounts.txt", "r") as f:
        for line in f:
            try:
                accounts.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return accounts


def get_last_checkin():
    """Read last checkin time from file."""
    if not os.path.exists(LAST_CHECKIN_FILE):
        return None

    with open(LAST_CHECKIN_FILE, "r") as f:
        raw_time = f.read().strip()
        if not raw_time:
            return None
        try:
            # Handles both "YYYY-MM-DD HH:MM:SS" and "YYYY-MM-DDTHH:MM:SS.ssssss"
            return datetime.fromisoformat(raw_time)
        except Exception:
            return None


def set_last_checkin():
    """Save current time as last checkin."""
    with open(LAST_CHECKIN_FILE, "w") as f:
        f.write(datetime.now().isoformat())


def checkin(account):
    """Perform checkin for a single account."""
    try:
        headers = {"Authorization": f"Bearer {account['token']}"}
        response = requests.post(f"{API_URL}/user/checkin", headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return f"[{account['username']}] ✅ Check-in success!"
            else:
                return f"[{account['username']}] ⚠️ Check-in failed: {data.get('message')}"
        else:
            return f"[{account['username']}] ❌ API error {response.status_code}"
    except Exception as e:
        return f"[{account['username']}] ❌ Error: {str(e)}"


def main():
    password_gate()
    accounts = load_accounts()

    if not accounts:
        print("⚠️ No accounts loaded. Add them in accounts.txt")
        return

    last_checkin = get_last_checkin()
    if last_checkin:
        delta = datetime.now() - last_checkin
        if delta.total_seconds() < 24 * 3600:
            print("⏳ Already checked in within 24 hours. Try later.")
            return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(checkin, acc) for acc in accounts]
        for future in futures:
            print(future.result())

    set_last_checkin()
    print("\n✅ All done! Next check-in after 24 hours.")


if __name__ == "__main__":
    main()
