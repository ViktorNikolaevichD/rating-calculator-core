from collections.abc import Iterable
from dataclasses import dataclass

from rating_kernel.domain.exceptions import ZeroTotalMarkWeightError
from rating_kernel.domain.value_objects.feedback import FeedbackMarkWithWeight


@dataclass(frozen=True)
class TotalMarkWeightAggregationPolicy:
    def apply(self, weights: Iterable[float]) -> float:
        return sum(weights)


@dataclass(frozen=True)
class WeightedAverageMarkScoreAggregationPolicy:
    def apply(self, marks_with_weights: Iterable[FeedbackMarkWithWeight]) -> float:
        weighted_marks_sum = 0.0
        total_weight = 0.0

        for mark_with_weight in marks_with_weights:
            weighted_marks_sum += mark_with_weight.value * mark_with_weight.weight
            total_weight += mark_with_weight.weight

        if total_weight == 0.0:
            raise ZeroTotalMarkWeightError("Невозможно рассчитать средневзвешенную оценку с нулевым общим весом")

        return weighted_marks_sum / total_weight
