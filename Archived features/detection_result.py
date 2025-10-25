class DetectionResults():
    def __init__(self, rule_name: str, is_suspicious: bool, confidence_score: float, details: str):
        self.rule_name = rule_name
        self.is_suspicious = is_suspicious
        self.confidence_score = confidence_score
        self.details = details