from src.i_detection_rule import IDecetionRule
import time
# from detection_result import DetectionResults archived


BOT_FREQUENTED_SUBREDDITS = {
    'nextfuckinglevel', 'publicfreakout', 'starterpacks', 'mademesmile',
    'interestingasfuck', 'askreddit', 'funny', 'mildlyinfuriating',
    'amitheasshole', 'oddlysatisfying', 'eyebleach', 'woahthatsinteresting',
    'meirl', 'me_irl', 'rareinsults', 'beamazed', 'memes', 'showerthoughts',
    'unpopularopinion', 'jokes', 'todayilearned', 'pics', 'holup',
    'thatsinsane', 'dankmemes', 'damnthatsinteresting', 'guysbeingdudes', 
    'murderedbywords', 'clevercomebacks', 'explainthejoke', 'peterexplainsthejoke',
    'interesting', 'sipstea', 'guysbeingdudes'
}
BOT_TYPICAL_TOPICS = {
    #crypto topics
    'crypto', 'blockchain', 'bitcoin', 'etherum', 'dogecoin', 'nft',
    #investing/moneymaking topics
    'stocks', 'wallstreet', 'pennystock', 'daytrade', 'forex', 
    'passiveincome', 'hustle', 'grind', 'dropship', 'money', 'buy'
    #etc
    'onlyfans', 'fansly', 'camgirl', 'shirt', 'hoodie', 'merch', 
    'essay', 'homework', 'vpn', 'nootropic', 'supplement', 'sarm', 'free',
    'nsfw'
}


class AccountSubbredditContentCheck(IDecetionRule):
    """
    This class determins patterns based on a users activity in certain subreddits

    Attributes:
        subreddits_frequents (set[str]): All the subreddits a user participates in based on the last 200 posts and 200 comments

    Values the class finds:
        1. The ratio of popular subreddit participation to all participation
        2. The ratio of scammy topic subreddit participation to all participation
    """
    def __init__(self, subreddits_frequents: set[str]):
        self.subreddits_frequents = subreddits_frequents
        self.subreddits_popular = BOT_FREQUENTED_SUBREDDITS
        self.subreddits_scammy = BOT_TYPICAL_TOPICS

    #returns the ratio of activity in popular subreddits
    def __check_popular_subbreddit_frequency__(self):
        if not self.subreddits_frequents:
            return 0
        total = 0
        for subreddit in self.subreddits_frequents:
            if subreddit in self.subreddits_popular:
                total += 1
        return total / len(self.subreddits_frequents)
    
    #returns the ratio of activity in scam/spam/profit subreddits
    def __check_scammy_subbreddit_frequency__(self):
        if not self.subreddits_frequents:
            return 0
        total = 0
        for user_subreddit in self.subreddits_frequents:
            for scam_keyword in self.subreddits_scammy:
                if scam_keyword in user_subreddit:
                    total += 1
                    break 
        return total / len(self.subreddits_frequents)
    
    def get_features(self) -> dict:
        features = {
            "popular_subreddits_ratio": self.__check_popular_subbreddit_frequency__(),
            "scammy_subreddits_ratio": self.__check_scammy_subbreddit_frequency__()
        }
        return features
    """
    def execute_check(self) -> DetectionResults:
        rule_name = "Popular Subreddit Check"
        popular_subreddits_ratio = self.__check_popular_subbreddit_frequency__()
        scammy_subreddits_ratio = self.__check_scammy_subbreddit_frequency__()
        confidence_score = (popular_subreddits_ratio * 0.7) + (scammy_subreddits_ratio * 1.0)
        confidence_score = min(confidence_score, 1.0)
        details = []
        if popular_subreddits_ratio > 0.15:
            details.append(f"~{popular_subreddits_ratio:.0%} of activity is in very large, generic subreddits.")
        if scammy_subreddits_ratio > 0.15:
            details.append(f"~{scammy_subreddits_ratio:.0%} of activity is in subreddits related to spam/scam topics (crypto, stocks, etc.).")
        is_suspicious = confidence_score > 0.35
        results = DetectionResults(
            rule_name = rule_name,
            is_suspicious = is_suspicious,
            confidence_score = confidence_score,
            details = " ".join(details)
        )
        return(results)
        """