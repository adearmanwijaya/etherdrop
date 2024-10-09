import requests
import json
import time
from datetime import datetime, timedelta
import random
from urllib.parse import parse_qs
from colorama import Fore, Style, init
import os
import platform
# Initialize colorama
init(autoreset=True)

# Global variables
start_time = datetime.now()



def print_welcome_message():
    print(Fore.WHITE + r"""
          
🆂🅸🆁🅺🅴🅻
          
█▀▀ █▀▀ █▄░█ █▀▀ █▀█ █▀█ █░█ █▀
█▄█ ██▄ █░▀█ ██▄ █▀▄ █▄█ █▄█ ▄█
          """)
    print(Fore.GREEN + Style.BRIGHT + "EtherDrop Bot")
    current_time = datetime.now()
    up_time = current_time - start_time
    days, remainder = divmod(up_time.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(Fore.CYAN + Style.BRIGHT + f"Up time bot: {int(days)} hari, {int(hours)} jam, {int(minutes)} menit, {int(seconds)} detik\n\n")

class DropstabClient:
    API_URL = "https://api.miniapp.dropstab.com"

    def __init__(self, query_data):
        self.token = None
        self.query_data = query_data
        self.account = self._parse_query_data()

    def _parse_query_data(self):
        parsed = parse_qs(self.query_data)
        account = {
            'query_id': parsed.get('query_id', [None])[0],
            'auth_date': parsed.get('auth_date', [None])[0],
            'hash': parsed.get('hash', [None])[0],
        }
        
        user_param = parsed.get('user', ['{}'])[0]
        user_data = json.loads(user_param)
        
        account.update({
            'user_id': int(user_data.get('id', 0)),
            'username': user_data.get('username', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'language_code': user_data.get('language_code', ''),
            'allow_write_to_pm': user_data.get('allows_write_to_pm', False)
        })
        
        return account

    def login(self):
        json_data = {"webAppData": self.query_data}  # Renamed to avoid confusion with the json module
        try:
            response = requests.post(f"{self.API_URL}/api/auth/login", json=json_data)  # Use json parameter
            response.raise_for_status()
            data = response.json()
            if "jwt" in data and "access" in data["jwt"] and "token" in data["jwt"]["access"]:
                self.token = data["jwt"]["access"]["token"]
                return True
            else:
                print(f"{Fore.RED+Style.BRIGHT}{self.account['username']} | Login failed: JWT structure not as expected{Style.RESET_ALL}")
                return False
        except requests.RequestException as e:
            print(f"{Fore.RED+Style.BRIGHT}{self.account['username']} | Login failed due to request error{Style.RESET_ALL}")
            return False

    def _make_authenticated_request(self, method, endpoint, payload=None):
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.API_URL}{endpoint}"
        # print(headers)
        try:
            response = requests.request(method, url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 400:
                # Attempt to parse the JSON response for more details
                try:
                    return response.json()
                    # print(f"{Fore.RED+Style.BRIGHT}{self.account['username']} | Request failed with 400: {error_details}{Style.RESET_ALL}")
                except json.JSONDecodeError:
                    print(f"{Fore.RED+Style.BRIGHT}         Request failed with 400 and no JSON response{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED+Style.BRIGHT} Request failed {e} {Style.RESET_ALL}")
            raise
        except requests.RequestException as e:
            print(f"{Fore.RED+Style.BRIGHT} Request failed {e} {Style.RESET_ALL}")
            raise

    def get_user_info(self):
        try:
            return self._make_authenticated_request("GET", "/api/user/current")
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}{self.account['username']} | Failed to get user info{Style.RESET_ALL}")
            return None
    
    def ghalibie(self):
        json_data = {"code": "7YU8Z"}
        try:
            return self._make_authenticated_request("PUT", "/api/user/applyRefLink", json_data)
        except requests.RequestException as e:
            print(f"{Fore.RED+Style.BRIGHT}Request failed: {e}{Style.RESET_ALL}")
            return None

    def daily_bonus(self):
        try:
            return self._make_authenticated_request("POST", "/api/bonus/dailyBonus")
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}[ Daily ]: Failed to claim daily bonus{Style.RESET_ALL}")
            return None
        
    def welcome_bonus(self):
        try:
            return self._make_authenticated_request("POST", "/api/bonus/welcomeBonus")
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}[ Welcome Bonus ]: Failed to claim daily bonus{Style.RESET_ALL}")
            return None

    def ether_drops_subscription(self):
        try:
            return self._make_authenticated_request("GET", "/api/etherDropsSubscription")
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}[ Balance]: Failed to get ether drops subscription{Style.RESET_ALL}")
            return None

    def ref_info(self):
        try:
            return self._make_authenticated_request("GET", "/api/refLink")
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}[ Refferal ]: Failed to get ref info{Style.RESET_ALL}")
            return None

    def claim_ref(self):
        try:
            result = self._make_authenticated_request("POST", "/api/refLink/claim")
            if result.get('status') == 'OK':
                print(f"{Fore.GREEN+Style.BRIGHT}[ Claim Reff ]: Claim Successfully{Style.RESET_ALL}")
            elif result.get('message') == 'Already claimed':
                print(f"{Fore.YELLOW+Style.BRIGHT}[ Claim Reff ]: Already Claimed{Style.RESET_ALL}")
            return result
        except requests.RequestException:
            return None

    def active_task_list(self):
        try:
            return self._make_authenticated_request("GET", "/api/quest")
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}[ Task ]: Failed to get active task list{Style.RESET_ALL}")
            return None

    def verify_task(self, task_id):
        try:
            result = self._make_authenticated_request("PUT", f"/api/quest/{task_id}/verify")
            return result.get('status', 'FAILED')
        except requests.RequestException:
            print(f"{Fore.RED+Style.BRIGHT}Error verifying task {task_id}{Style.RESET_ALL}")
            return 'FAILED'

    def claim_task(self, task_id):
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                result = self._make_authenticated_request("PUT", f"/api/quest/{task_id}/claim")
                if result.get('status') == 'OK':
                    return 'OK'
                elif result.get('code') == 'QUEST_NOT_COMPLETED':      
                    return 'QUEST_NOT_COMPLETED'
                else:
                    # print(f"{Fore.YELLOW+Style.BRIGHT}{self.account['username']} | Claim attempt {attempt+1} failed, retrying in {retry_delay} seconds...{Style.RESET_ALL}")
                    time.sleep(retry_delay)
            except requests.RequestException as e:
                print(f"{Fore.RED+Style.BRIGHT}          -> Request failed {e}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    print(f"{Fore.YELLOW+Style.BRIGHT}          -> Retrying in {retry_delay} seconds...{Style.RESET_ALL}")
                    time.sleep(retry_delay)
                else:
                    print(f"{Fore.YELLOW+Style.BRIGHT}          -> Failed to claim. May be Claimable in Next Loop.{Style.RESET_ALL}")
                    return 'FAILED'
        
        return 'FAILED'

    def auto_farming(self):
        points = 0
        if not self.login():
            return points

        user_info = self.get_user_info()
        if user_info:
            # balance = user_info['balance']
            # available_invites = user_info['availableInvites']
            # welcome_bonus_claimed = user_info['welcomeBonusReceived']
            # allow_ref = user_info['allowRefLink']
            print(f"{Fore.GREEN+Style.BRIGHT}========[ {Fore.WHITE}{self.account['username']}{Style.RESET_ALL}{Fore.GREEN+Style.BRIGHT} ]======== {Style.RESET_ALL}")
        else:
            print(f"{Fore.RED+Style.BRIGHT}=======[ User Info Not Found ]========={Style.RESET_ALL}")
            return points
        ghalibie = self.ghalibie()
        # print(ghalibie)
        if ghalibie is not None:
            if 'id' in ghalibie and 'tgId' in ghalibie:
                print(f"{Fore.GREEN+Style.BRIGHT}[ Refferal ]: Applied Successfully{Style.RESET_ALL}")
            elif ghalibie.get('code') == 'USER_ALREADY_APPLY_REF_LINK_ERROR':
                print(f"{Fore.RED+Style.BRIGHT}[ Refferal ]: Already Applied Before (NOT FRESH){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED+Style.BRIGHT}[ Refferal ]: Failed to apply referral{Style.RESET_ALL}")

        daily_bonus = self.daily_bonus()
        welcome = self.welcome_bonus()
        if welcome is not None:
            if welcome['result'] == False:
                print(f"{Fore.YELLOW+Style.BRIGHT}[ Welcome Bonus ]: Already Claimed{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN+Style.BRIGHT}[ Welcome Bonus ]: Successfully Claimed. Bonus: {welcome['bonus']}{Style.RESET_ALL}")
        if daily_bonus and daily_bonus.get('result'):
            print(f"{Fore.GREEN+Style.BRIGHT}[ Daily ]: Successfully Claimed Daily Bonus | Bonus: {daily_bonus['bonus']} | Streak: {daily_bonus['streaks']}{Style.RESET_ALL}")

        subscription = self.ether_drops_subscription()
        if subscription:
            print(f"{Fore.GREEN+Style.BRIGHT}[ Balance ]: {subscription['balance']} | Course: {subscription['course']} | Available: {subscription['available']} | Claimed: {len(subscription['claimed'])}{Style.RESET_ALL}")

        self.auto_claim_ref()
        self.process_tasks()

        final_user_info = self.get_user_info()
        if final_user_info:
            points = final_user_info['balance']

        return points

    def auto_claim_ref(self):
        ref_info = self.ref_info()
        if ref_info:
            print(f"{Fore.GREEN+Style.BRIGHT}[ Refferal ]: Ref Code: {ref_info.get('code')} | Total Ref: {ref_info['referrals'].get('total', 0)} | Total Reward: {ref_info.get('totalReward', 0)} | Available Claim: {ref_info.get('availableToClaim', 0)}{Style.RESET_ALL}")
            self.claim_ref()
            
            

    def process_tasks(self):
        active_tasks = self.active_task_list()
        if active_tasks:
            print(f"{Fore.YELLOW}[ Tasks ]: List of Active Tasks {Style.RESET_ALL}")
            
            has_non_invite_tasks = False
            for task in active_tasks:
                if 'quests' in task:
                    for quest in task['quests']:
                        if 'Invite' not in quest['name']:
                            has_non_invite_tasks = True
                            break
                    if has_non_invite_tasks:
                        break
            
            if not has_non_invite_tasks:
                print(f"{Fore.YELLOW+Style.BRIGHT}[ Tasks ]: Only invite tasks found. Skipping.{Style.RESET_ALL}")
                return
            
            # Process tasks one by one
            for task in active_tasks:
                if 'quests' in task:
                    for quest in task['quests']:
                        quest_name = quest['name']
                        quest_id = quest['id']
                        quest_status = quest['status']

                        
                        if 'Invite' in quest_name:
                            print(f"{Fore.YELLOW+Style.BRIGHT}          -> {quest_name} Skipped         {Style.RESET_ALL}")
                            continue
                        if quest_status == 'COMPLETED':
                            print(f"{Fore.GREEN+Style.BRIGHT}          -> {quest_name} Completed         {Style.RESET_ALL}")
                            continue
                        elif quest_status == 'VERIFICATION':
                            print(f"{Fore.CYAN+Style.BRIGHT}          -> {quest_name} Verification        {Style.RESET_ALL}")
                            continue
                        else:
                            print(f"{Fore.YELLOW+Style.BRIGHT}          -> {quest_name} Starting            {Style.RESET_ALL}", end="\r", flush=True)
                        
                        verify_result = self.verify_task(quest_id)
                        if verify_result == "OK":
                            print(f"{Fore.YELLOW+Style.BRIGHT}          -> {quest_name} Started            {Style.RESET_ALL}")
                            
                            # Wait for a longer time before attempting to claim
                            time.sleep(2)
                            
                            # Attempt to claim the task
                            claim_result = self.claim_task(quest_id)
                            if claim_result == "OK":
                                print(f"{Fore.GREEN+Style.BRIGHT}          -> {quest_name} Claimed       {Style.RESET_ALL}")
                            elif claim_result == "QUEST_NOT_COMPLETED":
                                print(f"{Fore.CYAN+Style.BRIGHT}          -> {quest_name} Quest in Verification {Style.RESET_ALL}")
                            else:
                                print(f"{Fore.YELLOW+Style.BRIGHT}          -> {quest_name} Failed to Claim. May be Claimable in Next Loop.{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED+Style.BRIGHT}          -> {quest_name} Failed to Start        {Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW+Style.BRIGHT}[ Tasks ]: No active tasks found.{Style.RESET_ALL}")

 
def process_accounts(query_file):
    total_points = 0
    account_count = 0
    
    with open(query_file, 'r') as file:
        queries = file.readlines()
    
    for query in queries:
        account_count += 1
        print(f"\n{Fore.CYAN+Style.BRIGHT}Processing Account {account_count}/{len(queries)}{Style.RESET_ALL}")
        client = DropstabClient(query.strip())
        points = client.auto_farming()
        total_points += points
        print(f"{Fore.GREEN+Style.BRIGHT}Account {account_count} Finished. Points: {points}{Style.RESET_ALL}")
        time.sleep(1)  # Wait 5 seconds between accounts
    
    return total_points, account_count

def main():
    print_welcome_message()

    query_file = "query.txt"  # File containing multiple queries, one per line
    total_points, account_count = process_accounts(query_file)
    
    print(f"\n{Fore.GREEN+Style.BRIGHT}All Accounts Processed{Style.RESET_ALL}")
    print(f"{Fore.GREEN+Style.BRIGHT}Total Accounts: {account_count}{Style.RESET_ALL}")
    print(f"{Fore.GREEN+Style.BRIGHT}Total Points: {total_points}{Style.RESET_ALL}")
    
    print(Fore.BLUE + Style.BRIGHT + f"\n{'='*20} ALL ACCOUNTS PROCESSED {'='*20}\n")
    
    for _ in range(1800):
        minutes, seconds = divmod(1800 - _, 60)
        print(f"{random.choice([Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE])+Style.BRIGHT}==== [ All accounts processed, Next loop in {minutes:02d}:{seconds:02d} ] ===={Style.RESET_ALL}", end="\r", flush=True)
        time.sleep(1)

if __name__ == "__main__":
    main()