from i_detection_rule import IDecetionRule
import praw
from detection_result import DetectionResults
import re

pattern = re.compile(
    r'^[A-Za-z][a-z]+(?:[_-][A-Za-z][a-z]+|[A-Z][a-z]+)(?:[_-])?\d{2,}$'
)

#Checks if the account 
# 1. Posts/Comments on the top subbreddits only

class AccountGeneralSearch(IDecetionRule):
    def __init__(self, reddit_user: praw.Reddit.redditor):
        self.verified_email = reddit_user.has_verified_email
        self.trophy_count = len(reddit_user.trophies())
        self.reddit_name = reddit_user.name

        self.PATTERN = pattern

        #cut offs for hueristics 
        self.TROPHY_THRESHOLD = 2 
    
    def __check_verified__(self):
        return self.verified_email
    def __check_trophies__(self):
        return self.trophy_count
    def __check_name__(self):
        return bool(pattern.fullmatch(self.reddit_name))
    def execute_check(self) -> DetectionResults:
        rule_name = "General Account Check"
        confidence_score = 0.0
        details = []

        is_verified = self.__check_verified__()
        if not is_verified:
            confidence_score += 0.4
            details.append("Account email is not verified.")

        trophy_count = self.__check_trophies__()
        if trophy_count < self.TROPHY_THRESHOLD:
            confidence_score += 0.3
            details.append(f"Account has fewer than {self.TROPHY_THRESHOLD} trophies ({trophy_count}).")

        has_bot_name = self.__check_name__()
        if has_bot_name:
            confidence_score += 0.3
            details.append("Account name matches a common bot pattern.")

        confidence_score = min(confidence_score, 1.0) 
        is_suspicious = confidence_score >= 0.5 

        results = DetectionResults(
            rule_name=rule_name,
            is_suspicious=is_suspicious,
            confidence_score=confidence_score,
            details=" ".join(details)
        )
        return results