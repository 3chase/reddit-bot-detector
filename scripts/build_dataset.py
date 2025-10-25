import praw
from dotenv import load_dotenv
import os
import csv
import time
from praw.exceptions import PRAWException
from prawcore.exceptions import NotFound, Forbidden

from src.user_data_fetcher import UserDataFetcher
from src.account_activity_check import AccountActivityCheck
from src.account_content_check import AccountContentCheck
from src.account_subbreddit_content_check import AccountSubbredditContentCheck
from src.account_general_search import AccountGeneralSearch
from data.known_bots import KNOWN_BOTS
from data.known_humans import KNOWN_HUMANS

load_dotenv()
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
user_agent = os.getenv("REDDIT_USER_AGENT")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")


reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent=user_agent)

OUTPUT_FILE = "training_data.csv"


FEATURE_COLUMNS = [
    "karma_ratio", #returns float of the ratio of post karma to comment karma
    "active_karma_rate", #returns float of the avg karma per day in the last 30 days or less of activity
    "age_days", #returns int of the age of the account in days
    "biggest_timestamp", #returns float the largest time between activity in Unix
    "burst_activity_ratio", #returns float of the ratio of activity that takes place within 65 seconds
    "first_activity_delay", #returns int of the days of how long it took from account creation to first activity
    "short_comment_ratio", #returns float of the ratio of comments under 20 characters
    "avg_comment_similarity", #returns float in the pairwise similarity score of the last 10 comments
    "verified_email", #returns a boolean of if the account has a verified email
    "trophy_count", #returns int of how many trophies an account has
    "name_pattern", #returns boolean if an account has a Word-Word-Num regex name pattern
    "icon_default", #returns boolean of if the account has the default icon
    "popular_subreddits_ratio", #returns the ratio of activity of common karma farming subreddits given a list of subs
    "scammy_subreddits_ratio" #returns the ratio of activity of scam/spam/selling subs given a list of keywords
]
# The full CSV header
CSV_HEADER = ["username", "is_bot"] + FEATURE_COLUMNS


def get_processed_users(filename: str) -> set:
    """Reads the CSV file to see which users we've already processed."""
    processed = set()
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                processed.add(row[0]) # Add username
    except FileNotFoundError:
        pass # File doesn't exist yet, that's fine
    return processed

def initialize_csv(filename: str):
    """Creates the CSV file with the header if it doesn't exist."""
    if not os.path.exists(filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            writer.writeheader()

def process_user(username: str, is_bot_label: int, writer: csv.DictWriter):
    """Fetches all data for a single user and writes it to the CSV."""
    print(f"Processing user: {username} (Label: {is_bot_label})")
    all_features = {key: None for key in FEATURE_COLUMNS}
    
    try:
        # 1. Get PRAW user object
        reddit_user = reddit.redditor(username)
        
        # 2. Fetch basic data
        fetcher = UserDataFetcher(reddit_user)
        user_info = fetcher.get_data()
        
        # 3. Run all checks and get features
        activity_check = AccountActivityCheck(user_info.comment_karma, user_info.link_karma, user_info.timestamps_and_karma, user_info.oldest_timestamp, user_info.account_timestamp)
        all_features.update(activity_check.get_features())
        
        subreddit_check = AccountSubbredditContentCheck(user_info.subreddits)
        all_features.update(subreddit_check.get_features())
        
        general_check = AccountGeneralSearch(user_info.verified_email, user_info.trophy_count, user_info.account_name, user_info.profile_picture)
        all_features.update(general_check.get_features())

        content_check = AccountContentCheck(user_info.account_name, user_info.comments, user_info.comments, reddit)
        all_features.update(content_check.get_features())

        # 5. Add username and label
        all_features["username"] = username
        all_features["is_bot"] = is_bot_label
        
        # 6. Write to CSV
        writer.writerow(all_features)
        print(f"  ... Successfully processed and saved {username}.")

    except (NotFound, Forbidden):
        print(f"  ... FAILED: User {username} not found or is suspended. Skipping.")
    except PRAWException as e:
        print(f"  ... FAILED: A PRAW error occurred for {username}: {e}. Skipping.")
    except Exception as e:
        # This catches Google API errors, rate limits, etc.
        print(f"  ... FAILED: An unexpected error occurred for {username}: {e}. Skipping.")


# --- Main Script ---

def main():
    initialize_csv(OUTPUT_FILE)
    processed_users = get_processed_users(OUTPUT_FILE)
    print(f"Found {len(processed_users)} users already in CSV.")

    # Combine all users into a list of (username, label) tuples
    users_to_process = []
    users_to_process.extend([(user, 1) for user in KNOWN_BOTS])   # Label 1 for bots
    users_to_process.extend([(user, 0) for user in KNOWN_HUMANS]) # Label 0 for humans

    # Open the file in append mode to add new users
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        
        total_new = 0
        for username, label in users_to_process:
            if username in processed_users:
                continue # Skip users we already have
            
            # Process the new user
            process_user(username, label, writer)
            total_new += 1
            
            # IMPORTANT: Polite sleep to not hammer Reddit's API
            time.sleep(2) 
            
            # You might still hit your Google API limit here and see an error.
            # If that happens, just re-run this script tomorrow.
            # It will skip all the users you've already done.

    print(f"\n--- Data Collection Complete ---")
    print(f"Processed {total_new} new users.")
    print(f"Total users in {OUTPUT_FILE}: {len(get_processed_users(OUTPUT_FILE))}")

if __name__ == "__main__":
    main()