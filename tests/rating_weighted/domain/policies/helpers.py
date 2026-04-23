from datetime import datetime, timedelta

from rating_kernel.domain.value_objects.feedback import (
    Feedback,
    FeedbackContent,
    FeedbackMark,
    FeedbackModerationState,
    FeedbackTimingContext,
)
from rating_kernel.domain.value_objects.reviewer import (
    Reviewer,
    ReviewerActivityProfile,
    ReviewerIdentity,
    ReviewerReputationHistory,
)
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


def make_feedback_mark_context(
    *,
    mark_value: float = 5.0,
    text: str | None = "valid text",
    text_has_template: bool = False,
    has_flag: bool = False,
    reviews_left_in_24h: int = 0,
    now: datetime | None = None,
    last_repeat: datetime | None = None,
) -> FeedbackMarkContext:
    current_time = _make_current_time(now)
    repeat_time = _make_last_repeat_time(current_time, last_repeat)
    reviewer = _make_reviewer(reviews_left_in_24h)
    feedback = _make_feedback(
        mark_value=mark_value,
        text=text,
        text_has_template=text_has_template,
        has_flag=has_flag,
        repeat_time=repeat_time,
        reviewer=reviewer,
    )

    return FeedbackMarkContext(
        feedback=feedback,
        mark=FeedbackMark(value=mark_value),
        now=current_time,
    )


def _make_current_time(now: datetime | None = None) -> datetime:
    return now or datetime(2026, 4, 23, 12, 0, 0)


def _make_last_repeat_time(current_time: datetime, last_repeat: datetime | None = None) -> datetime:
    return last_repeat or current_time - timedelta(days=30)


def _make_reviewer(reviews_left_in_24h: int) -> Reviewer:
    return Reviewer(
        identity=ReviewerIdentity(is_verified=True, has_flag=False),
        activity=ReviewerActivityProfile(
            days_since_registration=365,
            number_of_reviews_left_in_24h=reviews_left_in_24h,
            unique_targets=20,
        ),
        reputation=ReviewerReputationHistory(
            approved_reviews=100,
            deleted_reviews_history_in_30d=0,
            received_likes_on_feedbacks=50,
            received_dislikes_on_feedbacks=5,
        ),
    )


def _make_feedback(
    *,
    mark_value: float,
    text: str | None,
    text_has_template: bool,
    has_flag: bool,
    repeat_time: datetime,
    reviewer: Reviewer,
) -> Feedback:
    return Feedback(
        content=FeedbackContent(marks=(FeedbackMark(value=mark_value),), text=text),
        moderation=FeedbackModerationState(text_has_template=text_has_template, has_flag=has_flag),
        timing=FeedbackTimingContext(last_repeat=repeat_time),
        reviewer=reviewer,
    )
