from dataclasses import dataclass
from math import log

from rating_kernel.domain.value_objects.reviewer import Reviewer
from rating_weighted.domain.value_objects.configuration import TemporalConfig


@dataclass(frozen=True)
class AccountAgeFactorPolicy:
    coefficient: float
    max_days_for_full_score: int = 30

    def apply(self, reviewer: Reviewer) -> float:
        days = reviewer.activity.days_since_registration

        return min(
            days / self.max_days_for_full_score,
            1.0,
        )

    def contribution(self, reviewer: Reviewer) -> float:
        return self.coefficient * self.apply(reviewer)


@dataclass(frozen=True)
class FeedbackExperienceFactorPolicy:
    coefficient: float

    def apply(self, reviewer: Reviewer) -> float:
        approved_reviews = reviewer.reputation.approved_reviews

        return min(
            log(1 + approved_reviews) / log(1 + 20),
            1.0,
        )

    def contribution(self, reviewer: Reviewer) -> float:
        return self.coefficient * self.apply(reviewer)


@dataclass(frozen=True)
class UsefulnessFactorPolicy:
    coefficient: float

    def apply(self, reviewer: Reviewer) -> float:
        likes = reviewer.reputation.received_likes_on_feedbacks
        dislikes = reviewer.reputation.received_dislikes_on_feedbacks

        return (likes + 1) / (likes + dislikes + 1)

    def contribution(self, reviewer: Reviewer) -> float:
        return self.coefficient * self.apply(reviewer)


@dataclass(frozen=True)
class AccountVerificationFactorPolicy:
    coefficient: float

    def apply(self, reviewer: Reviewer) -> float:
        return 1.0 if reviewer.identity.is_verified else 0.0

    def contribution(self, reviewer: Reviewer) -> float:
        return self.coefficient * self.apply(reviewer)


@dataclass(frozen=True)
class ActivityDiversityFactorPolicy:
    coefficient: float
    max_unique_targets_for_full_score: int = 10

    def apply(self, reviewer: Reviewer) -> float:
        unique_targets = reviewer.activity.unique_targets

        return min(
            unique_targets / self.max_unique_targets_for_full_score,
            1.0,
        )

    def contribution(self, reviewer: Reviewer) -> float:
        return self.coefficient * self.apply(reviewer)


@dataclass(frozen=True)
class LongTermAccountRiskFactorPolicy:
    config: TemporalConfig
    coefficient: float
    account_flag_ratio: float = 0.6
    deleted_reviews_history_ratio: float = 0.4

    def apply(self, reviewer: Reviewer) -> float:
        account_flag = 0.0
        deleted_reviews_history = 0.0

        if reviewer.identity.has_flag:
            account_flag = self.account_flag_ratio

        if reviewer.reputation.deleted_reviews_history_in_30d > self.config.deleted_reviews_limit_for_period:
            deleted_reviews_history = self.deleted_reviews_history_ratio

        return account_flag + deleted_reviews_history

    def contribution(self, reviewer: Reviewer) -> float:
        return self.coefficient * self.apply(reviewer)
