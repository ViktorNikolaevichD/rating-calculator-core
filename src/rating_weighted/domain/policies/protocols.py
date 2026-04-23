from typing import Protocol

from rating_kernel.domain.value_objects.feedback import FeedbackMarkWithWeight
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext
from rating_weighted.domain.value_objects.rating_context import RatingContext


class PenaltyPolicy(Protocol):
    def apply(self, context: FeedbackMarkContext) -> float: ...


class TrustFactorPolicy(Protocol):
    def apply(self, context: RatingContext) -> float: ...


class FeedbackWeightAggregationPolicy(Protocol):
    def apply(self, trust_score: float, total_penalty: float) -> float: ...


class TotalMarkWeightAggregationPolicy(Protocol):
    def apply(self, weights: tuple[float, ...]) -> float: ...


class WeightedAverageMarkScoreAggregationPolicy(Protocol):
    def apply(self, marks_with_weights: tuple[FeedbackMarkWithWeight, ...]) -> float: ...
