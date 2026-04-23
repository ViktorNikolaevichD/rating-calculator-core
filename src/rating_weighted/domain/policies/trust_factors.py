from dataclasses import dataclass
from math import log

from rating_weighted.domain.value_objects.configuration import TemporalConfig
from rating_weighted.domain.value_objects.rating_context import RatingContext


@dataclass(frozen=True)
class AccountAgeFactorPolicy:
    max_days_for_full_score: int = 30

    def apply(self, context: RatingContext) -> float:
        days = context.feedback.reviewer.activity.days_since_registration

        return min(
            days / self.max_days_for_full_score,
            1.0,
        )


@dataclass(frozen=True)
class FeedbackExperienceFactorPolicy:
    def apply(self, context: RatingContext) -> float:
        approved_reviews = context.feedback.reviewer.reputation.approved_reviews

        return min(
            log(1 + approved_reviews) / log(1 + 20),
            1.0,
        )


@dataclass(frozen=True)
class UsefulnessFactorPolicy:
    def apply(self, context: RatingContext) -> float:
        likes = context.feedback.reviewer.reputation.received_likes_on_feedbacks
        dislikes = context.feedback.reviewer.reputation.received_dislikes_on_feedbacks

        return (likes + 1) / (likes + dislikes + 1)


@dataclass(frozen=True)
class AccountVerificationFactorPolicy:
    def apply(self, context: RatingContext) -> float:
        return 1.0 if context.feedback.reviewer.identity.is_verified else 0.0


@dataclass(frozen=True)
class ActivityDiversityFactorPolicy:
    max_unique_targets_for_full_score: int = 10

    def apply(self, context: RatingContext) -> float:
        unique_targets = context.feedback.reviewer.activity.unique_targets

        return min(
            unique_targets / self.max_unique_targets_for_full_score,
            1.0,
        )


@dataclass(frozen=True)
class LongTermAccountRiskFactorPolicy:
    config: TemporalConfig
    account_flag_ratio: float = 0.6
    deleted_reviews_history_ratio: float = 0.4

    def apply(self, context: RatingContext) -> float:
        account_flag = 0.0
        deleted_reviews_history = 0.0

        if context.feedback.reviewer.identity.has_flag:
            account_flag = self.account_flag_ratio
        
        if context.feedback.reviewer.reputation.deleted_reviews_history_in_30d > self.config.deleted_reviews_limit_for_period:
            deleted_reviews_history = self.deleted_reviews_history_ratio

        return account_flag + deleted_reviews_history
