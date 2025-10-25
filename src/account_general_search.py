from src.i_detection_rule import IDecetionRule
import praw
#from detection_result import DetectionResults archived
import re

PATTERN = re.compile(
    #Returns if the username is a pattern like AngryDog22 or angry_dog-22 (Reddit default is Angry-Dog-1495)
    r'^[A-Za-z][a-z]+(?:[_-][A-Za-z][a-z]+|[A-Z][a-z]+)(?:[_-])?\d{2,}$'
)

class AccountGeneralSearch(IDecetionRule):
    """
    This class gets related information of a user relating general account information to make decisions

    Attributes:
        verified_email (bool): Returns if user email is verfied for the account
        trophy_count (int): The amount of trophies a account has earned (different from reddit achievements)
        reddit_name (str): The user name of the account
        profile_picture (str): The image link of the profile picture

    Values the class finds:
        1. The boolean of if the user has a verifed email
        2. The amount of trophies an user has on the account
        3. The boolean of if the name of the reddit user matches the regex pattern
        4. The boolean if a reddit user has a default profile picture
    """
    def __init__(self, verified_email: bool, trophy_count: int, reddit_name: str, profile_picture: str):
        self.verified_email = verified_email
        self.trophy_count = trophy_count
        self.reddit_name = reddit_name
        self.profile_picture = profile_picture
        self.PATTERN = PATTERN

        #cut offs for hueristics 
        self.TROPHY_THRESHOLD = 2 
    
    def __check_verified__(self):
        return self.verified_email
    def __check_trophies__(self):
        return self.trophy_count
    def __check_name__(self):
        return bool(self.PATTERN.fullmatch(self.reddit_name))
    def __check_icon__(self):
        if not isinstance(self, AccountGeneralSearch):
            return False
        return "/avatars/defaults/" in self.profile_picture #link for the defualt reddit profile picture
    def get_features(self) -> dict:
        features = {
            "verified_email": 1 if self.__check_verified__() else 0,
            "trophy_count": self.__check_trophies__(),
            "name_pattern": 1 if self.__check_name__() else 0,
            "icon_default": 1 if self.__check_icon__() else 0
        }
        return features
    


    """
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
        """