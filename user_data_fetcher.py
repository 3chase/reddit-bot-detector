from praw.models import Redditor
import datetime

class UserProfile():
    def __init__(self, account_name: str, account_age: float, timestamps: list[float],comments: list[str],
                  subreddits: list[str], comment_karma: int, link_karma: int):
        self.account_name = account_name
        self.account_age = account_age
        self.timestamps = timestamps
        self.comments = comments
        self.subreddits = subreddits
        self.comment_karma = comment_karma
        self.link_karma = link_karma

class UserDataFetcher:
    def __init__(self, reddit_user: Redditor):
        self.reddit_user = reddit_user
    def __get_name__(self):
        return self.reddit_user.name
    def __get_age__(self):
        age = self.reddit_user.created_utc
        return age
    def __get_timestamps__(self):
        all_timestamps = []
        try:
            for item in self.reddit_user.new(limit=900):
                all_timestamps.append(item.created_utc)
        except Exception as e:
            print(f"Debug: Error fetching user.new(): {e}")
            return []
        return all_timestamps
    def __get_comments__(self):
        all_comments = []
        for comment in self.reddit_user.comments.new(limit=500):
            all_comments.append(comment.body)
        return all_comments
    def __get_user_post_and_comments_subreddits__(self):
        subreddits = set()
        for submission in self.reddit_user.submissions.new(limit=50):
            subreddits.add(submission.subreddit.display_name.lower())
        for comment in self.reddit_user.comments.new(limit=50):
            subreddits.add(comment.subreddit.display_name.lower())
        return list(subreddits)
    def __get_comment_karma__(self):
        return self.reddit_user.comment_karma
    def __get_link_karma__(self):
        return self.reddit_user.link_karma
    def get_data(self) -> UserProfile:
        results = UserProfile(
            account_name = self.__get_name__(),
            account_age = self.__get_age__(),
            timestamps = self.__get_timestamps__(),
            comments = self.__get_comments__(),
            subreddits = self.__get_user_post_and_comments_subreddits__(),
            comment_karma = self.__get_comment_karma__(),
            link_karma = self.__get_link_karma__()
        )
        return results

    