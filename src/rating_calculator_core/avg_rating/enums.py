from enum import Enum as PyEnum


class OrganizationFeedbackNatureOfFeedback(PyEnum):
    NEGATIVE = "negative"
    POSITIVE = "positive"

    def __str__(self) -> str:
        return self.value


class NatureOfFeedbacks(PyEnum):
    NEGATIVE = "negative"
    MOSTLY_NEGATIVE = "mostly_negative"
    MIXED = "mixed"
    MOSTLY_POSITIVE = "mostly_positive"
    POSITIVE = "positive"

    def __str__(self) -> str:
        return self.value
