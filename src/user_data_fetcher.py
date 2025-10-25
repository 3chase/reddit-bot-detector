from praw.models import Redditor
import datetime
import requests


class UserProfile():
    """ This class is what stores all the user data fetched

    Attributes:
        account_name (str): The name of the reddit account
        account_timestamp (float): Unix timestamp of the reddit account
        timestamp_posts_comments_karma (list[(float,float)]): A list of pairs of an accounts last up to 900 posts and comments. Each value in the list
                                                                is one post/comment and the pair stores (timestamp of the post/comment, karma of the post/comment)
        oldest_timestamp (float): The Unix timestamp of a reddit's account first activity
        comments (list[str]): the 50 most recents comments of a account
        subreddits (set[str]): All the subreddits a user participates in based on the last 200 posts and 200 comments
        comment_karma (int): An integer representing the karma the account has from commenting
        link_karma (int): An integer representing the karma the account has from posting
        verified_email (bool): Returns if user email is verfied for the account
        trophy_count (int): The amount of trophies a account has earned (different from reddit achievements)
        profile_picture (str): The image link of the profile picture
    """
    def __init__(self, account_name: str, account_timestamp: float, timestamps_and_karma: list[(float, float)], oldest_timestamp: float,
                 comments: list[str], subreddits: list[str], comment_karma: int, link_karma: int, verified_email: bool, 
                 trophy_count: int, profile_picture: str):
        self.account_name = account_name
        self.account_timestamp = account_timestamp
        self.timestamps_and_karma = timestamps_and_karma
        self.oldest_timestamp = oldest_timestamp
        self.comments = comments
        self.subreddits = subreddits
        self.comment_karma = comment_karma
        self.link_karma = link_karma
        self.verified_email = verified_email
        self.trophy_count = trophy_count
        self.profile_picture = profile_picture
        
class UserDataFetcher:
    """This class makes the API calls with praw to fetch the related reddit users information

        Attributes: 
            reddit_user (praw.Reddit.Redditor): An authenticated PRAW Reddit instance of a Redditor class

    """
    def __init__(self, reddit_user: Redditor):
        self.reddit_user = reddit_user
    def __get_name__(self):
        return self.reddit_user.name
    def __get_timestamp__(self):
        timestamp = self.reddit_user.created_utc
        return timestamp
    def __get_timestamps_and_karma__(self):
        all_timestamps_and_karma = []
        try:
            for item in self.reddit_user.new(limit=900):
                all_timestamps_and_karma.append((item.created_utc, item.score))
        except Exception as e:
            print(f"Debug: Error fetching user.new(): {e}")
            return []
        return all_timestamps_and_karma
    

    def __get_oldest_timestamp__(self):
        base = "https://arctic-shift.photon-reddit.com/api/{}/search"
        params = {"author": self.reddit_user.name, "sort": "asc", "limit": 1}

        oldest_activity = float("inf") 

        for kind in ("comments", "submissions"):
            try:
                r = requests.get(base.format(kind), params=params, timeout=5)
                r.raise_for_status()
                data = r.json().get("data") or []
                if data:
                    ts = data[0].get("created_utc")
                    if ts is not None:
                        oldest_activity = min(oldest_activity, float(ts)) 
            except requests.RequestException:
                continue
        return -1 if oldest_activity == float("inf") else int(oldest_activity)
    def __get_comments__(self):
        all_comments = []
        for comment in self.reddit_user.comments.new(limit=500):
            all_comments.append(comment.body)
        return all_comments
    def __get_user_post_and_comments_subreddits__(self):
        subreddits = set()
        for submission in self.reddit_user.submissions.new(limit=200):
            subreddits.add(submission.subreddit.display_name.lower())
        for comment in self.reddit_user.comments.new(limit=200):
            subreddits.add(comment.subreddit.display_name.lower())
        return list(subreddits)
    def __get_comment_karma__(self):
        return self.reddit_user.comment_karma
    def __get_link_karma__(self):
        return self.reddit_user.link_karma
    def __check_verified_email__(self):
        return self.reddit_user.has_verified_email
    def __get_trophy_amount__(self):
        return len(self.reddit_user.trophies())
    def __get_profile_picture__(self):
        return self.reddit_user.icon_img
    def get_data(self) -> UserProfile:
        results = UserProfile(
            account_name = self.__get_name__(),
            account_timestamp = self.__get_timestamp__(),
            timestamps_and_karma = self.__get_timestamps_and_karma__(),
            oldest_timestamp = self.__get_oldest_timestamp__(),
            comments = self.__get_comments__(),
            subreddits = self.__get_user_post_and_comments_subreddits__(),
            comment_karma = self.__get_comment_karma__(),
            link_karma = self.__get_link_karma__(),
            verified_email = self.__check_verified_email__(),
            trophy_count = self.__get_trophy_amount__(),
            profile_picture = self.__get_profile_picture__()
        )
        return results

    