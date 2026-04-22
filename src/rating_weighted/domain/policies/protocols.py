from typing import Protocol

from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


class PenaltyPolicy(Protocol):
    def apply(self, context: FeedbackMarkContext) -> float: ...
