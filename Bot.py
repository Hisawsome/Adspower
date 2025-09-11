import sys
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

# Initialize colorama and rich console
init(autoreset=True)
console = Console()

# Display logo
def display_logo():
    logo_text = Text("   BY RIDI   ", style="bold yellow", justify="center")
    footer_text = Text("© 2025 — Private Build", style="cyan", justify="center")
    combined_text = logo_text + Text("\n\n") + footer_text
    panel = Panel(combined_text, title="🚀 BOT STARTED 🚀", border_style="green", width=70)
    console.print(panel)

# Password check
def password_check():
    console.print("[bold cyan]Enter password to unlock bot:[/bold cyan]")
    pwd = input("Password: ").strip()
    if pwd != "RIDI":
        print(f"{Fore.RED}❌ Wrong password. Exiting...{Style.RESET_ALL}")
        sys.exit(1)

# ==========================
#  MAIN BOT CODE STARTS HERE
# ==========================

# File to store check-in timestamps
CHECKIN_FILE = "checkin_timestamps.json"

def read_user_ids(file_path='id.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Error reading id.txt: {e}{Style.RESET_ALL}")
        return []

def read_init_datas(file_path='data.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Error reading data.txt: {e}{Style.RESET_ALL}")
        return []

def load_checkin_timestamps():
    if os.path.exists(CHECKIN_FILE):
        try:
            with open(CHECKIN_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_checkin_timestamps(timestamps):
    try:
        with open(CHECKIN_FILE, 'w') as f:
            json.dump(timestamps, f)
    except Exception as e:
        print(f"{Fore.RED}Error saving timestamps: {e}{Style.RESET_ALL}")

def checkin(user_id, init_data, checkin_timestamps):
    now = datetime.now()
    last_checkin_time = checkin_timestamps.get(user_id)
    if last_checkin_time:
        last_checkin_time = datetime.strptime(last_checkin_time, '%Y-%m-%d %H:%M:%S')
        if now - last_checkin_time < timedelta(hours=24):
            return f"{Fore.YELLOW}User {user_id}: Already checked in within the last 24 hours.{Style.RESET_ALL}"

    url = "https://api.hamsterkombatgame.io/clicker/boost/checkin"
    headers = {"Content-Type": "application/json"}
    data = {"user_id": user_id, "init_data": init_data}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            checkin_timestamps[user_id] = now.strftime('%Y-%m-%d %H:%M:%S')
            save_checkin_timestamps(checkin_timestamps)
            return f"{Fore.GREEN}User {user_id}: Check-in successful!{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}User {user_id}: Failed to check-in, Status Code: {response.status_code}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}User {user_id}: Error during check-in: {e}{Style.RESET_ALL}"

def main():
    user_ids = read_user_ids()
    init_datas = read_init_datas()
    checkin_timestamps = load_checkin_timestamps()

    if not user_ids or not init_datas:
        print(f"{Fore.RED}No user_ids or init_datas found.{Style.RESET_ALL}")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(checkin, user_id, init_data, checkin_timestamps)
                   for user_id, init_data in zip(user_ids, init_datas)]
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    password_check()   # 🔐 Ask for RIDI before starting
    display_logo()
    while True:
        main()
        print(f"{Fore.CYAN}Sleeping for 60 minutes before next check-in...{Style.RESET_ALL}")
        time.sleep(3600)
