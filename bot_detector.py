import praw
from dotenv import load_dotenv
import os
from account_activity_check import AccountActivityCheck
from user_data_fetcher import UserDataFetcher
from account_content_check import AccountContentCheck
from account_subbreddit_content_check import AccountSubbredditContentCheck
from account_general_search import AccountGeneralSearch

load_dotenv()
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
user_agent = os.getenv("REDDIT_USER_AGENT")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")

reddit = praw.Reddit(client_id = client_id, 
                     client_secret = client_secret, 
                     username = username, 
                     password = password,
                     user_agent = user_agent) 
target_sub = "reddit_bot_test"
trigger_phrase = "!CheckForBot"
subreddit = reddit.subreddit(target_sub)

#list of bot accounts TelephoneNorth2971, CarpetLongjumping876, PerformanceHot6349
def main():
    reddit_user = reddit.redditor("Few-Olive-6259")
    
    current_query = UserDataFetcher(reddit_user)
    user_info = current_query.get_data()
    current_query = AccountActivityCheck(user_info.comment_karma, user_info.link_karma, user_info.timestamps, user_info.account_age)
    results = current_query.execute_check()
    print(f"--- Detection Results ---")
    print(f"Rule: {results.rule_name}")
    print(f"Suspicious: {results.is_suspicious}")
    print(f"Confidence Score: {results.confidence_score:.0%}")
    print(f"Details: {results.details}")
    print(f"-----------------------")
    

    """
    current_query = AccountSubbredditContentCheck(user_info.subreddits)
    results = current_query.execute_check()
    print(f"--- Detection Results ---")
    print(f"Rule: {results.rule_name}")
    print(f"Suspicious: {results.is_suspicious}")
    print(f"Confidence Score: {results.confidence_score:.0%}")
    print(f"Details: {results.details}")
    print(f"-----------------------")
    """

   
    
    current_query = AccountContentCheck(user_info.account_name, user_info.comments, user_info.comments, reddit)
    results = current_query.execute_check()
    print(f"--- Detection Results ---")
    print(f"Rule: {results.rule_name}")
    print(f"Suspicious: {results.is_suspicious}")
    print(f"Confidence Score: {results.confidence_score:.0%}")
    print(f"Details: {results.details}")
    print(f"-----------------------")

    current_query = AccountGeneralSearch(reddit_user)
    results = current_query.execute_check()
    print(f"--- Detection Results ---")
    print(f"Rule: {results.rule_name}")
    print(f"Suspicious: {results.is_suspicious}")
    print(f"Confidence Score: {results.confidence_score:.0%}")
    print(f"Details: {results.details}")
    print(f"-----------------------")
    
    

            
if __name__ == "__main__":
    main()


"""# check every comment in the subreddit
    for comment in subreddit.stream.comments():
        # check the trigger_phrase in each comment
        if trigger_phrase in comment.body:"""