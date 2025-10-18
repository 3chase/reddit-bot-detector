from abc import ABC, abstractmethod
from detection_result import DetectionResults

class IDecetionRule(ABC):
    @abstractmethod
    def execute_check(user_profile) -> DetectionResults:
        pass

    