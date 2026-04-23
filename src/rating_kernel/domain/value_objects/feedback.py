from dataclasses import dataclass
from datetime import datetime

from rating_kernel.domain.value_objects.reviewer import Reviewer


@dataclass(frozen=True)
class FeedbackMark:
    value: float


@dataclass(frozen=True)
class FeedbackMarkWithWeight:
    value: float
    weight: float


@dataclass(frozen=True)
class FeedbackContent:
    marks: tuple[FeedbackMark, ...]
    text: str | None


@dataclass(frozen=True)
class FeedbackModerationState:
    text_has_template: bool
    has_flag: bool


@dataclass(frozen=True)
class FeedbackTimingContext:
    last_repeat: datetime


@dataclass(frozen=True)
class Feedback:
    content: FeedbackContent
    moderation: FeedbackModerationState
    timing: FeedbackTimingContext
    reviewer: Reviewer
