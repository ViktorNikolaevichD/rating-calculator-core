from typing import Protocol

from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext
from rating_weighted.domain.value_objects.rating_context import RatingContext


class PenaltyPolicy(Protocol):
    def apply(self, context: FeedbackMarkContext) -> float: ...


class TrustFactorPolicy(Protocol):
    def apply(self, context: RatingContext) -> float: ...
