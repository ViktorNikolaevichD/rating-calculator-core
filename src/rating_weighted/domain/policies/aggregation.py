from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class PenaltyAggregationPolicy:
    max_total: float

    def apply(self, penalties: Iterable[float]) -> float:
        return min(sum(penalties), self.max_total)
