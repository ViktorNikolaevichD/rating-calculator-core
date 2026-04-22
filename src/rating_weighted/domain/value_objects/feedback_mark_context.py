from dataclasses import dataclass
from datetime import datetime

from rating_kernel.domain.value_objects.feedback import Feedback, FeedbackMark


@dataclass(frozen=True)
class FeedbackMarkContext:
    feedback: Feedback
    mark: FeedbackMark
    now: datetime
