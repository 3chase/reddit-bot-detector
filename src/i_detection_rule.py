from abc import ABC, abstractmethod
#from detection_result import DetectionResults       #Old import

class IDecetionRule(ABC):
    @abstractmethod
    def get_features(self) -> dict:
        pass

    