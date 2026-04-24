from dataclasses import dataclass
from datetime import datetime

from rating_kernel.domain.value_objects.feedback import Feedback, FeedbackWithMarkWeights
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


@dataclass(frozen=True)
class RatingContext:
    feedback: Feedback
    now: datetime

    def per_mark_contexts(self) -> tuple[FeedbackMarkContext, ...]:
        return tuple(
            FeedbackMarkContext(feedback=self.feedback, now=self.now, mark=mark)
            for mark in self.feedback.content.marks
        )


@dataclass(frozen=True)
class RatingContextWithMarkWeights:
    feedback: FeedbackWithMarkWeights
    now: datetime
