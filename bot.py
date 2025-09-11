import requests
import json
import time
import threading
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

# === Init ===
init(autoreset=True)
console = Console()

# === Password protection ===
PASSWORD = "RIDI"
entered = input("Enter password to start bot: ")
if entered.strip() != PASSWORD:
    print("❌ Wrong password. Exiting...")
    exit(1)
print("✅ Access granted. Bot starting...\n")

# === File storage ===
CHECKIN_FILE = "checkin_timestamps.json"

# === Display branding ===
def display_logo():
    logo_text = Text(" RIDI CHECKIN BOT ", style="bold yellow", justify="center")
    team_text = Text("By Ridi", style="bold green", justify="center")
    footer_text = Text("All rights reserved.", style="cyan", justify="center")
    combined_text = logo_text + Text("\n\n") + team_text + Text("\n") + footer_text
    panel = Panel(combined_text, title="🚀 BOT START 🚀", border_style="red", width=90)
    console.print(panel)

display_logo()
print("\n")

# === Loaders ===
def read_init_datas(file_path="data.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Error reading {file_path}: {e}{Style.RESET_ALL}")
        return []

def read_user_ids(file_path="id.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Error reading {file_path}: {e}{Style.RESET_ALL}")
        return []

# === Timestamp storage ===
def load_checkin_timestamps():
    if os.path.exists(CHECKIN_FILE):
        with open(CHECKIN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checkin_timestamps(timestamps):
    with open(CHECKIN_FILE, "w") as f:
        json.dump(timestamps, f)

# === Check-in ===
def checkin(user_id, init_data, timestamps):
    try:
        last_checkin_time = timestamps.get(user_id)
        if last_checkin_time:
            last_checkin_time = datetime.fromisoformat(last_checkin_time)
            if datetime.now() - last_checkin_time < timedelta(hours=24):
                return f"{Fore.YELLOW}[{user_id}] Already checked in within 24h.{Style.RESET_ALL}"

        # Example API request
        url = "https://example.com/api/checkin"
        payload = {"id": user_id, "init_data": init_data}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            timestamps[user_id] = datetime.now().isoformat()
            save_checkin_timestamps(timestamps)
            return f"{Fore.GREEN}[{user_id}] Check-in successful ✅{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}[{user_id}] Check-in failed ❌ ({response.status_code}){Style.RESET_ALL}"

    except Exception as e:
        return f"{Fore.RED}[{user_id}] Error: {e}{Style.RESET_ALL}"

# === Main ===
def main():
    init_datas = read_init_datas()
    user_ids = read_user_ids()
    timestamps = load_checkin_timestamps()

    if not init_datas or not user_ids:
        print("⚠️ No accounts loaded. Make sure data.txt and id.txt are filled in.")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(checkin, user_id, init_datas[i % len(init_datas)], timestamps)
                   for i, user_id in enumerate(user_ids)]
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    main()
