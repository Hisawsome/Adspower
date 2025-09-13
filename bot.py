import time;print('NOT FOR SALE');time.sleep(2.5)
import requests
import json
import time
import threading
import os
import sys  # Added for exiting the script
import getpass # Added for secure password input
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

# Initialize colorama and rich console
init(autoreset=True)
console = Console()

# --- ADDED PASSWORD CHECK ---
CORRECT_PASSWORD = "BY RIDI"
try:
    password = getpass.getpass("Enter the password: ")
    if password != CORRECT_PASSWORD:
        print(f"{Fore.RED}Incorrect password. Exiting.{Style.RESET_ALL}")
        sys.exit()
    else:
        print(f"{Fore.GREEN}Password correct. Starting bot...{Style.RESET_ALL}")
        time.sleep(1.5)
except KeyboardInterrupt:
    print(f"\n{Fore.YELLOW}Operation cancelled by user. Exiting.{Style.RESET_ALL}")
    sys.exit()
# --- END OF PASSWORD CHECK ---


# Display logo
def display_logo():
    logo_text = Text("   BY RIDI   ", style="bold yellow", justify="center")
    footer_text = Text("© 2025 — Private Build", style="cyan", justify="center")
    combined_text = logo_text + Text("\n\n") + footer_text
    panel = Panel(combined_text, title="🚀 BOT STARTED 🚀", border_style="green", width=70)
    console.print(panel)

display_logo()
print("\n")


# File to store check-in timestamps
CHECKIN_FILE = "checkin_timestamps.json"

# Function to read user_ids from id.txt
def read_user_ids(file_path='id.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Error reading id.txt: {e}{Style.RESET_ALL}")
        return []

# Function to read init_datas from data.txt
def read_init_datas(file_path='data.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Error reading data.txt: {e}{Style.RESET_ALL}")
        return []

# Function to load check-in timestamps
def load_checkin_timestamps():
    if not os.path.exists(CHECKIN_FILE):
        print(f"{Fore.YELLOW}Creating new checkin_timestamps.json{Style.RESET_ALL}")
        return {}
    try:
        with open(CHECKIN_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error reading {CHECKIN_FILE}: {e}. Starting with empty timestamps.{Style.RESET_ALL}")
        return {}

# Function to save check-in timestamps
def save_checkin_timestamps(timestamps):
    try:
        with open(CHECKIN_FILE, 'w') as f:
            json.dump(timestamps, f, indent=4)
    except Exception as e:
        print(f"{Fore.RED}Error saving {CHECKIN_FILE}: {e}{Style.RESET_ALL}")

# Shared headers
def get_headers():
    return {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        'Accept': "application/json",
        'Content-Type': "application/json",
        'sec-ch-ua-platform': "\"Windows\"",
        'sec-ch-ua': "\"Chromium\";v=\"139\", \"Microsoft Edge WebView2\";v=\"139\", \"Microsoft Edge\";v=\"139\", \"Not;A=Brand\";v=\"99\"",
        'sec-ch-ua-mobile': "?0",
        'origin': "https://adsevm.saifpowersoft.top",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://adsevm.saifpowersoft.top/cards.php",
        'accept-language': "en-US,en;q=0.9",
        'priority': "u=1, i"
    }

# Function to fetch dashboard data
def fetch_dashboard(user_id, init_data, headers):
    url = "https://adsevm.saifpowersoft.top/api/dashboard.php"
    payload = {
        "user_id": user_id,
        "init_data": init_data
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"{Fore.RED}Error fetching dashboard for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Exception fetching dashboard for user {user_id}: {e}{Style.RESET_ALL}")
        return None

# Function to claim a task
def claim_task(user_id, init_data, task_id, headers):
    url = "https://adsevm.saifpowersoft.top/api/claim.php"
    payload = {
        "user_id": user_id,
        "task_id": task_id,
        "init_data": init_data
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            card_type = data.get('card_type', '')
            print(f"{Fore.GREEN}Claim for task: {message} | Card Type: {card_type}{Style.RESET_ALL}")
            return data
        else:
            print(f"{Fore.RED}Error claiming task for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Exception claiming task for user {user_id}: {e}{Style.RESET_ALL}")
        return None

# Function to scratch a card
def scratch_card(user_id, init_data, card_id, headers):
    url = "https://adsevm.saifpowersoft.top/api/scratch.php"
    payload = {
        "user_id": user_id,
        "init_data": init_data,
        "card_id": card_id
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            print(f"{Fore.YELLOW}Scratch for card: {message}{Style.RESET_ALL}")
            return data
        else:
            print(f"{Fore.RED}Error scratching card for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Exception scratching card for user {user_id}: {e}{Style.RESET_ALL}")
        return None

# Function to perform daily check-in
def perform_checkin(user_id, init_data, headers):
    url = "https://adsevm.saifpowersoft.top/cards.php?action=do_checkin"
    payload = {
        "user_id": user_id,
        "init_data": init_data
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == "error" and data.get('message') == "Already checked in today":
                print(f"{Fore.RED}Check-in failed for user {user_id}: Already checked in today{Style.RESET_ALL}")
                return False
            else:
                print(f"{Fore.CYAN}Daily check-in successful for user {user_id}: {data.get('message', 'Success')}{Style.RESET_ALL}")
                return True
        else:
            print(f"{Fore.RED}Error during check-in for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Exception during check-in for user {user_id}: {e}{Style.RESET_ALL}")
        return False

# Function to watch ad
def watch_ad(user_id, init_data, network, headers):
    url = "https://adsevm.saifpowersoft.top/api/watched.php"
    payload = {
        "user_id": user_id,
        "init_data": init_data,
        "network": network
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()
            reward = data.get('reward', '0')
            # Fetch updated balance and ad limits
            dashboard = fetch_dashboard(user_id, init_data, headers)
            balance = dashboard['user_details'].get('balance', '0') if dashboard else 'Unknown'
            network_data = dashboard.get('user_tasks', {}).get(network, {})
            ads_watched_today = network_data.get('ads_watched_today', 0)
            daily_limit = network_data.get('daily_limit', 50)
            ads_watched_hourly = network_data.get('ads_watched_hourly', 0)
            hourly_limit = network_data.get('hourly_limit', 50)
            daily_remaining = daily_limit - ads_watched_today
            hourly_remaining = hourly_limit - ads_watched_hourly
            print(f"{Fore.CYAN}Ad watched for user {user_id}: Reward: {reward} $ADS, New Balance: {balance}, Daily Ads Remaining: {daily_remaining}, Hourly Ads Remaining: {hourly_remaining}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Debug: Network={network}, Daily: {ads_watched_today}/{daily_limit}, Hourly: {ads_watched_hourly}/{hourly_limit}, Reward: {reward}{Style.RESET_ALL}")
            return data
        else:
            print(f"{Fore.RED}Error watching ad for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Exception watching ad for user {user_id}: {e}{Style.RESET_ALL}")
        return None

# Function to handle tasks for a single account
def handle_tasks(user_id, init_data, acc_name, headers):
    dashboard = fetch_dashboard(user_id, init_data, headers)
    if not dashboard or not dashboard.get('ok'):
        print(f"{Fore.RED}Failed to fetch dashboard for {acc_name}{Style.RESET_ALL}")
        return []

    name = dashboard['user_details'].get('name', 'Unknown')
    balance = dashboard['user_details'].get('balance', '0')
    print(f"{Fore.BLUE}{acc_name} - Name: {name}, Balance: {balance}{Style.RESET_ALL}")

    # Extract task_ids
    tasks = dashboard.get('tasks', [])
    task_ids = [task['task_id'] for task in tasks]

    # Claim tasks with 15s delay
    for i, task_id in enumerate(task_ids):
        claim_task(user_id, init_data, task_id, headers)
        if i < len(task_ids) - 1:  # Don't print wait message after last task
            print(f"{Fore.MAGENTA}Waiting 15 seconds before next task...{Style.RESET_ALL}")
            time.sleep(15)  # 15s between claims

    return task_ids

# Function to handle scratches for a single account
def handle_scratches(user_id, init_data, acc_name, headers):
    dashboard = fetch_dashboard(user_id, init_data, headers)
    if not dashboard or not dashboard.get('ok'):
        print(f"{Fore.RED}Failed to fetch dashboard for scratches for {acc_name}{Style.RESET_ALL}")
        return

    # Extract and scratch cards
    scratch_cards = dashboard.get('scratch_card', [])
    for i, card in enumerate(scratch_cards):
        card_id = card.get('card_id')
        if card_id:
            scratch_card(user_id, init_data, card_id, headers)
            if i < len(scratch_cards) - 1:  # Don't print wait message after last card
                print(f"{Fore.MAGENTA}Waiting 15 seconds before next scratch...{Style.RESET_ALL}")
                time.sleep(15)  # 15s between scratches

# Function to handle daily check-in with 12-hour cooldown
def handle_checkin(user_id, init_data, acc_name, headers, timestamps):
    current_time = datetime.now()
    last_checkin = timestamps.get(str(user_id))
    if last_checkin:
        try:
            last_checkin_time = datetime.fromisoformat(last_checkin)
            if current_time < last_checkin_time + timedelta(hours=12):
                time_remaining = (last_checkin_time + timedelta(hours=12) - current_time).total_seconds()
                print(f"{Fore.RED}Check-in on cooldown for {acc_name}. Time remaining: {int(time_remaining // 3600)} hours, {int((time_remaining % 3600) // 60)} minutes.{Style.RESET_ALL}")
                return
        except ValueError as e:
            print(f"{Fore.RED}Invalid timestamp format for user {user_id} in {CHECKIN_FILE}: {e}. Attempting check-in.{Style.RESET_ALL}")

    if perform_checkin(user_id, init_data, headers):
        timestamps[str(user_id)] = current_time.isoformat()
        save_checkin_timestamps(timestamps)
    else:
        # If check-in fails due to "Already checked in today", still save timestamp
        timestamps[str(user_id)] = current_time.isoformat()
        save_checkin_timestamps(timestamps)

# Function to handle ads for a single account and network
def handle_ads_for_network(user_id, init_data, network, headers, hourly_cooldowns):
    while True:
        dashboard = fetch_dashboard(user_id, init_data, headers)
        if not dashboard or not dashboard.get('ok'):
            print(f"{Fore.RED}Failed to fetch dashboard for ads for user {user_id}{Style.RESET_ALL}")
            return False, False  # can_continue, daily_limit_reached

        user_tasks = dashboard.get('user_tasks', {})
        network_data = user_tasks.get(network, {})
        ads_watched_today = network_data.get('ads_watched_today', 0)
        ads_watched_hourly = network_data.get('ads_watched_hourly', 0)
        daily_limit = network_data.get('daily_limit', 50)
        hourly_limit = network_data.get('hourly_limit', 50)

        print(f"{Fore.YELLOW}Debug: Starting {network} for user {user_id}: Daily={ads_watched_today}/{daily_limit}, Hourly={ads_watched_hourly}/{hourly_limit}{Style.RESET_ALL}")

        if ads_watched_today >= daily_limit:
            print(f"{Fore.MAGENTA}Daily limit reached for user {user_id} (Daily: {ads_watched_today}/{daily_limit}, Hourly: {ads_watched_hourly}/{hourly_limit}). Stopping this network.{Style.RESET_ALL}")
            return False, True  # Stop this network, daily limit reached
        if ads_watched_hourly >= hourly_limit:
            print(f"{Fore.MAGENTA}Hourly limit reached for user {user_id} (Hourly: {ads_watched_hourly}/{hourly_limit}, Daily: {ads_watched_today}/{daily_limit}). Waiting 1 hour for this network.{Style.RESET_ALL}")
            hourly_cooldowns[network] = datetime.now() + timedelta(hours=1)
            return True, False  # Continue to next network, daily limit not reached

        # Watch ad
        ad_result = watch_ad(user_id, init_data, network, headers)
        if not ad_result:
            print(f"{Fore.MAGENTA}Ad watch failed for {network}. Switching to next network.{Style.RESET_ALL}")
            return True, False  # Continue to next network, daily limit not reached

        reward = float(ad_result.get('reward', '0'))
        # Re-fetch dashboard to confirm limits after ad watch
        dashboard = fetch_dashboard(user_id, init_data, headers)
        if dashboard and dashboard.get('ok'):
            network_data = dashboard.get('user_tasks', {}).get(network, {})
            ads_watched_today = network_data.get('ads_watched_today', 0)
            ads_watched_hourly = network_data.get('ads_watched_hourly', 0)
            if reward == 0:
                print(f"{Fore.MAGENTA}Reward is 0 for user {user_id} (Daily: {ads_watched_today}/{daily_limit}, Hourly: {ads_watched_hourly}/{hourly_limit}). Waiting 1 hour for this network.{Style.RESET_ALL}")
                hourly_cooldowns[network] = datetime.now() + timedelta(hours=1)
                return True, False  # Wait 1 hour, daily limit not reached
            if ads_watched_hourly >= hourly_limit:
                print(f"{Fore.MAGENTA}Hourly limit reached for user {user_id} (Hourly: {ads_watched_hourly}/{hourly_limit}, Daily: {ads_watched_today}/{daily_limit}). Waiting 1 hour for this network.{Style.RESET_ALL}")
                hourly_cooldowns[network] = datetime.now() + timedelta(hours=1)
                return True, False  # Hourly limit reached, daily limit not reached
            if ads_watched_today >= daily_limit:
                print(f"{Fore.MAGENTA}Daily limit reached for user {user_id} (Daily: {ads_watched_today}/{daily_limit}, Hourly: {ads_watched_hourly}/{hourly_limit}). Stopping this network.{Style.RESET_ALL}")
                return False, True  # Stop this network, daily limit reached
            print(f"{Fore.MAGENTA}Waiting 30 seconds before next ad...{Style.RESET_ALL}")
            time.sleep(30)  # 30s between ads
        return True, False  # Continue with this network, daily limit not reached

# Function to handle ads for a single account
def handle_ads(user_id, init_data, acc_name, headers):
    networks = ['adexium', 'gigapub', 'monetag']
    hourly_cooldowns = {}  # Track cooldown end times for each network

    while True:
        # Check if all networks have reached their daily limits
        all_daily_limits_reached = True
        any_network_processed = False

        for network in networks:
            # Skip network if it's on hourly cooldown
            if network in hourly_cooldowns:
                if datetime.now() < hourly_cooldowns[network]:
                    time_remaining = (hourly_cooldowns[network] - datetime.now()).total_seconds()
                    print(f"{Fore.MAGENTA}Network {network} on hourly cooldown for {acc_name}. Time remaining: {int(time_remaining // 60)} minutes, {int(time_remaining % 60)} seconds.{Style.RESET_ALL}")
                    # Check if this network has daily ads remaining
                    dashboard = fetch_dashboard(user_id, init_data, headers)
                    if dashboard and dashboard.get('ok'):
                        network_data = dashboard.get('user_tasks', {}).get(network, {})
                        ads_watched_today = network_data.get('ads_watched_today', 0)
                        daily_limit = network_data.get('daily_limit', 50)
                        if ads_watched_today < daily_limit:
                            all_daily_limits_reached = False
                    continue
                else:
                    del hourly_cooldowns[network]  # Cooldown expired, remove it

            # Process ads for the network
            can_continue, daily_limit_reached = handle_ads_for_network(user_id, init_data, network, headers, hourly_cooldowns)
            if can_continue:
                any_network_processed = True
            if not daily_limit_reached:
                all_daily_limits_reached = False

        if all_daily_limits_reached:
            print(f"{Fore.MAGENTA}All ad networks' daily limits reached for {acc_name}. Waiting 12 hours.{Style.RESET_ALL}")
            time.sleep(12 * 3600)  # Wait 12 hours when all daily limits are reached
            break
        elif not any_network_processed and hourly_cooldowns:
            # If no networks were processed (all on cooldown), wait for the earliest cooldown
            earliest_cooldown = min(hourly_cooldowns.values())
            wait_time = (earliest_cooldown - datetime.now()).total_seconds()
            if wait_time > 0:
                print(f"{Fore.MAGENTA}Waiting for earliest hourly cooldown to expire in {int(wait_time // 60)} minutes, {int(wait_time % 60)} seconds for {acc_name}.{Style.RESET_ALL}")
                time.sleep(wait_time)

# Function to process a single account with sequential threads
def process_account(acc_index, user_id, init_data, timestamps):
    acc_name = f"acc{acc_index + 1}"
    headers = get_headers()

    # Thread for tasks
    tasks_thread = threading.Thread(target=handle_tasks, args=(user_id, init_data, acc_name, headers))
    tasks_thread.start()
    tasks_thread.join()  # Wait for tasks to complete

    # Thread for scratches
    scratches_thread = threading.Thread(target=handle_scratches, args=(user_id, init_data, acc_name, headers))
    scratches_thread.start()
    scratches_thread.join()  # Wait for scratches to complete

    # Thread for check-in
    checkin_thread = threading.Thread(target=handle_checkin, args=(user_id, init_data, acc_name, headers, timestamps))
    checkin_thread.start()
    checkin_thread.join()  # Wait for check-in to complete

    # Thread for ads
    ads_thread = threading.Thread(target=handle_ads, args=(user_id, init_data, acc_name, headers))
    ads_thread.start()
    ads_thread.join()  # Wait for ads to complete

# Main entry
def main():
    user_ids = read_user_ids()
    init_datas = read_init_datas()

    if len(user_ids) != len(init_datas):
        print(f"{Fore.RED}Mismatch between id.txt and data.txt lengths.{Style.RESET_ALL}")
        return

    # Load check-in timestamps
    timestamps = load_checkin_timestamps()

    # Use ThreadPoolExecutor for multi-account threading
    with ThreadPoolExecutor(max_workers=len(user_ids)) as executor:
        futures = [executor.submit(process_account, i, user_ids[i], init_datas[i], timestamps) for i in range(len(user_ids))]
        for future in as_completed(futures):
            future.result()  # Wait for all to complete

    # Save timestamps after all accounts are processed
    save_checkin_timestamps(timestamps)

    # Wait 12 hours before next cycle
    print(f"{Fore.MAGENTA}All accounts processed. Waiting 12 hours for next cycle.{Style.RESET_ALL}")
    time.sleep(12 * 3600)

if __name__ == "__main__":
    while True:
        main()
