from i_detection_rule import IDecetionRule
import time
import datetime
from detection_result import DetectionResults

#Checks if the account 
# 1. Is under a week old
# 2. There is a long gap in activity (limited to 500 posts and 500 comments)
class AccountActivityCheck(IDecetionRule):
    def __init__(self, comment_karma: int, link_karma: int, timestamp_posts_comments: list[float], account_age: float):
        self.comment_karma = comment_karma
        self.post_karma = link_karma
        self.timestamp_posts_comments = timestamp_posts_comments
        self.account_age = account_age

        #constants
        self.HALF_A_YEAR_IN_SECONDS = 183 * 24 * 60 * 60
        self.ONE_MONTH_IN_SECONDS = 35 * 24 * 60 * 60 #a little over a month to try to catch bots that wait a month before posting

        #cut offs for hueristics 
        self.RATIO_THRESHOLD = 0.95 #for post karma to comment karma
        self.RATE_THRESHOLD = 2000 #karma per day
        self.RATE_MAX_SCALE = 10000 

    def __check_karma_ratio(self):
        total_karma = self.post_karma + self.comment_karma
        if total_karma == 0:
            return 0.0
        return self.post_karma / total_karma
    
    def __check_karma_rate(self):
        past_date = datetime.datetime.fromtimestamp(self.account_age)
        now = datetime.datetime.now()
        days_old = (now - past_date).days
        if days_old <= 0:
            days_old = 1
        karma_rate = (self.post_karma + self.comment_karma) / days_old
        return karma_rate

    #Returns true if the account age was created less then a week ago
    def __check_age__(self):
        current_unix_time = time.time()
        difference = current_unix_time - self.account_age
        return(difference <= self.ONE_MONTH_IN_SECONDS)
    #Returns true if the account has a one year gap in activity
    def __check_timestamps__(self):
        timestamps = self.timestamp_posts_comments
        if len(timestamps) < 2:
            return False
        consecutive_pairs = zip(timestamps, timestamps[1:])
        return any(t1 - t2 >= self.HALF_A_YEAR_IN_SECONDS for t1, t2 in consecutive_pairs)
    
    def __check_frequency_posting_(self):
        timestamps = self.timestamp_posts_comments
        n = len(timestamps)
        count = 0
        if n < 3:
            return 0
        for i in range(n - 2):
            if timestamps[i] - timestamps[i + 2] <= 20.0: 
                count += 1
        return count
        
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
        

        
    