from src.i_detection_rule import IDecetionRule
import time
import datetime
#from detection_result import DetectionResults archived

"""Add entropy of timestamps"""

class AccountActivityCheck(IDecetionRule):
    """This class gets related information of a user relating with 
    time of posts and the account, and also the features of the user's karma

    Attributes:
        comment_karma (int): An integer representing the karma the account has from commenting
        link_karma (int): An integer representing the karma the account has from posting
        timestamp_posts_comments_karma (list[(float,float)]): A list of pairs of an accounts last up to 900 posts and comments. Each value in the list
                                                                is one post/comment and the pair stores (timestamp of the post/comment, karma of the post/comment)
        oldest_timestamp (float): The timestamp of the first (not deleted) activity on a account
        account_timestamp (float): The timestamp of when the account was created

    Values the class finds:
        1. Post karma to total karma ratio
        2. Average karma earned per day rate in the latest 30 days of activity
        3. The account's age in days
        4. The max gap in activity (spans only the most recent 900 posts/comments)
        5. The ratio of the amount of bursts of activity within 65 seconds (spans only the most recent 900 posts/comments)
        6. The time between the account was created, and the first activity on the account
    """
    def __init__(self, comment_karma: int, link_karma: int, timestamp_posts_comments_karma: list[(float,float)], oldest_timestamp: float, account_timestamp: float):
        self.comment_karma = comment_karma
        self.post_karma = link_karma
        self.timestamp_posts_comments_karma = timestamp_posts_comments_karma
        self.oldest_timestamp = oldest_timestamp
        self.account_timestamp = account_timestamp

        #constants
        self.HALF_A_YEAR_IN_SECONDS = 183 * 24 * 60 * 60
        self.ONE_MONTH_IN_SECONDS = 30 * 24 * 60 * 60 
        self.ONE_YEAR_IN_SECONDS = 365 * 24 * 60 * 60
        
        #cut offs for hueristics 
        self.RATIO_THRESHOLD = 0.95 #for post karma to comment karma
        self.RATE_THRESHOLD = 2000 #karma per day
        self.RATE_MAX_SCALE = 10000 


    def __get_karma_ratio__(self):
        total_karma = self.post_karma + self.comment_karma
        if total_karma == 0:
            return 0.0
        return self.post_karma / total_karma
    
    
    def __get_active_karma_rate__(self):
        """Finds the average karma per day an account has earned in its recent 'active' window

            An active window is now to the closest timestamp of activity account has to 30 days back
        """
        if not self.timestamp_posts_comments_karma:
            return 0.0
        now = time.time()
        start_of_window = now - self.ONE_MONTH_IN_SECONDS
        total_recent_karma = 0.0
        oldest_recent_timestamp = None
        for timestamp, karma in self.timestamp_posts_comments_karma:
            if timestamp < start_of_window:
                break
            total_recent_karma += karma
            oldest_recent_timestamp = timestamp 
        if oldest_recent_timestamp is None:
            return 0.0
        active_period_seconds = now - oldest_recent_timestamp
        active_period_days = max(active_period_seconds / (24 * 60 * 60), 1)
        return total_recent_karma / active_period_days
    
    def __get_age_days__(self):
        now = time.time()
        age_seconds = now - self.account_timestamp
        return age_seconds / (24 * 60 * 60)

    def __get__max_timestamp__(self):
        """Gets the largest period of inactivity of a account between its timestamps
        """
        timestamps = [item[0] for item in self.timestamp_posts_comments_karma]
        if len(timestamps) < 2:
            return 0 
        consecutive_pairs = zip(timestamps, timestamps[1:])
        gaps = [t1 - t2 for t1, t2 in consecutive_pairs]
        return max(gaps) if gaps else 0
    
    def __get_burst_activity_ratio__(self):
        """Finds the amount of activity sent within a 65 second window of the last activity
        """
        threshold_seconds = 65
        activities = self.timestamp_posts_comments_karma
        num_activities = len(activities)
        if num_activities < 2:
            return 0.0
        burst_count = 0
        for i in range(num_activities - 1):
            time_gap = activities[i][0] - activities[i+1][0]
            if time_gap <= threshold_seconds:
                burst_count += 1
        burst_ratio = burst_count / (num_activities - 1)
        return burst_ratio
    
    def __get_first_activity_delay_days__(self):
        oldest_activity_ts = self.oldest_timestamp
        if oldest_activity_ts == -1:
            return 0
        account_creation_ts = self.account_timestamp 
        difference_seconds = oldest_activity_ts - account_creation_ts
        if difference_seconds < 0:
            return 0
        return difference_seconds / (24 * 60 * 60)
    
    def get_features(self) -> dict:
        features = {
            "karma_ratio": self.__get_karma_ratio__(),
            "active_karma_rate": self.__get_active_karma_rate__(),
            "age_days": self.__get_age_days__(),
            "biggest_timestamp": self.__get__max_timestamp__(),
            "burst_activity_ratio": self.__get_burst_activity_ratio__(),
            "first_activity_delay": self.__get_first_activity_delay_days__()
        }
        return features



#Old code for manual weights 
"""
    def execute_check(self) -> DetectionResults:
        rule_name = "Account Age and Activity Gaps, and Karma Behavior"
        confidence_score = 0.0
        details = []

        timestamps_gap_check = self.__check_timestamps__() 
        creation_age_check = self.__check_age__()
        karma_ratio = self.__check_karma_ratio()
        karma_rate = self.__check_karma_rate()
        frequency_check = self.__check_frequency_posting_()
        
        score_from_gap = 0
        if timestamps_gap_check:
            score_from_gap = 0.6
            details.append("Account has a >6 month activity gap.")

        score_from_rapid_fire = 0.0
        if frequency_check > 2:
            score_from_rapid_fire = 0.3
            details.append(f"Has {frequency_check} periods of rapid fire posting")
        
        score_from_post_ratio = 0.0
        if karma_ratio > self.RATIO_THRESHOLD:
            scaled_ratio = (karma_ratio - self.RATIO_THRESHOLD) / (1.0 - self.RATIO_THRESHOLD)
            score_from_post_ratio = scaled_ratio * 0.3  
            details.append(f"High post-to-comment karma ratio ({karma_ratio:.0%}).")
        
        score_from_karma_rate = 0.0
        if karma_rate > self.RATE_THRESHOLD:
            scaled_rate = (karma_rate - self.RATE_THRESHOLD) / (self.RATE_MAX_SCALE - self.RATE_THRESHOLD)
            scaled_rate = min(scaled_rate, 1.0)
            score_from_karma_rate = scaled_rate * 0.3 
            details.append(f"High karma rate ({karma_rate:,.0f}/day).")

        score_from_newness_interaction = 0.0
        if creation_age_check:
            details.append("Account is less than 1 month old.")
            if score_from_karma_rate > 0:
                score_from_newness_interaction += 0.3
            if score_from_post_ratio > 0:
                score_from_newness_interaction += 0.3

        confidence_score = (
            score_from_gap + 
            score_from_rapid_fire +
            score_from_post_ratio + 
            score_from_karma_rate + 
            score_from_newness_interaction
        )

        confidence_score = min(confidence_score, 1.0)
        is_suspicious = confidence_score >= 0.5

        results = DetectionResults(
            rule_name=rule_name,
            is_suspicious=is_suspicious,
            confidence_score=confidence_score,
            details=" ".join(details)
        )
        return(results)
""" 

        
    