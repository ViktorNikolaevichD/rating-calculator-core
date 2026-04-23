from collections.abc import Iterable
from dataclasses import dataclass

from rating_weighted.domain.value_objects.configuration import AggregatedPenaltyConfig


@dataclass(frozen=True)
class PenaltyAggregationPolicy:
    config: AggregatedPenaltyConfig

    def apply(self, penalties: Iterable[float]) -> float:
        return min(sum(penalties), self.config.maximum_total_feedback_penalty)
