from typing import Protocol

from rating_kernel.domain.value_objects.feedback import FeedbackMarkWithWeight
from rating_kernel.domain.value_objects.reviewer import Reviewer
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


class PenaltyPolicy(Protocol):
    def apply(self, context: FeedbackMarkContext) -> float: ...


class TrustFactorPolicy(Protocol):
    def apply(self, reviewer: Reviewer) -> float: ...


class FeedbackWeightAggregationPolicy(Protocol):
    def apply(self, trust_score: float, total_penalty: float) -> float: ...


class TotalMarkWeightAggregationPolicy(Protocol):
    def apply(self, weights: tuple[float, ...]) -> float: ...


class WeightedAverageMarkScoreAggregationPolicy(Protocol):
    def apply(self, marks_with_weights: tuple[FeedbackMarkWithWeight, ...]) -> float: ...


class BaseRatingContributionPolicy(Protocol):
    def apply(self, base_rating: float, total_mark_weight: float) -> float: ...


class ReviewerTrustContributionPolicy(Protocol):
    def apply(self, weighted_average_mark: float, total_mark_weight: float) -> float: ...


class FinalRatingAggregationPolicy(Protocol):
    def apply(self, base_rating_contribution: float, reviewer_trust_contribution: float) -> float: ...
