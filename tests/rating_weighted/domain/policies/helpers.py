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
from rating_weighted.domain.value_objects.rating_context import RatingContext


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


def make_rating_context(
    *,
    is_verified: bool = True,
    has_flag: bool = False,
    days_since_registration: int = 30,
    unique_targets: int = 10,
    approved_reviews: int = 20,
    deleted_reviews_history_in_30d: int = 0,
    received_likes_on_feedbacks: int = 5,
    received_dislikes_on_feedbacks: int = 0,
    now: datetime | None = None,
) -> RatingContext:
    current_time = _make_current_time(now)
    reviewer = _make_rating_reviewer(
        is_verified=is_verified,
        has_flag=has_flag,
        days_since_registration=days_since_registration,
        unique_targets=unique_targets,
        approved_reviews=approved_reviews,
        deleted_reviews_history_in_30d=deleted_reviews_history_in_30d,
        received_likes_on_feedbacks=received_likes_on_feedbacks,
        received_dislikes_on_feedbacks=received_dislikes_on_feedbacks,
    )
    feedback = _make_rating_feedback(current_time=current_time, reviewer=reviewer)

    return RatingContext(feedback=feedback, now=current_time)


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


def _make_rating_reviewer(
    *,
    is_verified: bool,
    has_flag: bool,
    days_since_registration: int,
    unique_targets: int,
    approved_reviews: int,
    deleted_reviews_history_in_30d: int,
    received_likes_on_feedbacks: int,
    received_dislikes_on_feedbacks: int,
) -> Reviewer:
    return Reviewer(
        identity=ReviewerIdentity(is_verified=is_verified, has_flag=has_flag),
        activity=ReviewerActivityProfile(
            days_since_registration=days_since_registration,
            number_of_reviews_left_in_24h=0,
            unique_targets=unique_targets,
        ),
        reputation=ReviewerReputationHistory(
            approved_reviews=approved_reviews,
            deleted_reviews_history_in_30d=deleted_reviews_history_in_30d,
            received_likes_on_feedbacks=received_likes_on_feedbacks,
            received_dislikes_on_feedbacks=received_dislikes_on_feedbacks,
        ),
    )


def _make_rating_feedback(*, current_time: datetime, reviewer: Reviewer) -> Feedback:
    return Feedback(
        content=FeedbackContent(marks=(FeedbackMark(value=5.0),), text="text"),
        moderation=FeedbackModerationState(text_has_template=False, has_flag=False),
        timing=FeedbackTimingContext(last_repeat=current_time),
        reviewer=reviewer,
    )
