import praw
from dotenv import load_dotenv
import os
import joblib
import numpy as np

# Import all your check classes and UserDataFetcher
from src.user_data_fetcher import UserDataFetcher
from src.account_activity_check import AccountActivityCheck
from src.account_content_check import AccountContentCheck
from src.account_subbreddit_content_check import AccountSubbredditContentCheck
from src.account_general_search import AccountGeneralSearch


class BotDetector:
    def __init__(self, praw_instance):
        self.praw_instance = praw_instance
        self.model = joblib.load("models/bot_detector_model.pkl")
        

        self.feature_cols_order = [
            "karma_ratio",
            "active_karma_rate",
            "age_days",
            "biggest_timestamp",
            "burst_activity_ratio",
            "first_activity_delay",
            "short_comment_ratio",
            "avg_comment_similarity",
            "verified_email",
            "trophy_count",
            "name_pattern",
            "icon_default",
            "popular_subreddits_ratio",
            "scammy_subreddits_ratio"
        ]

    def get_all_features(self, reddit_user, user_info) -> dict:
        """Gathers all raw features from all check classes."""
        all_features = {}

        activity_check = AccountActivityCheck(user_info.comment_karma, user_info.link_karma, user_info.timestamps_and_karma, user_info.oldest_timestamp, user_info.account_timestamp)
        all_features.update(activity_check.get_features()) 

        content_check = AccountContentCheck(user_info.account_name, user_info.comments, user_info.comments, self.praw_instance)
        all_features.update(content_check.get_features())

        subreddit_check = AccountSubbredditContentCheck(user_info.subreddits)
        all_features.update(subreddit_check.get_features())

        general_check = AccountGeneralSearch(user_info.verified_email, user_info.trophy_count, user_info.account_name, user_info.profile_picture)
        all_features.update(general_check.get_features())

        return all_features

    def check_user(self, username: str):
        reddit_user = self.praw_instance.redditor(username)

        user_data_fetcher = UserDataFetcher(reddit_user)
        user_info = user_data_fetcher.get_data()

        features_dict = self.get_all_features(reddit_user, user_info)

        feature_vector = [features_dict[col] for col in self.feature_cols_order]
        feature_vector = [1 if v is True else (0 if v is False else v) for v in feature_vector]
        

        final_features = np.array(feature_vector).reshape(1, -1)

        probability = self.model.predict_proba(final_features)
        
        confidence_score = probability[0][1] # Get the probability of being a bot
        is_suspicious = confidence_score > 0.5 

        print(f"--- Detection Results for {username} ---")
        print(f"Suspicious: {is_suspicious}")
        print(f"Confidence Score: {confidence_score:.0%}")
        print(f"-----------------------")

def main():
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
    detector = BotDetector(reddit)

    detector.check_user("TheAttraction-Signal") 
    detector.check_user("GoldenRaptorGaming")
    detector.check_user("biznatch11")

if __name__ == "__main__":
    main()