from dataclasses import dataclass

@dataclass(frozen=True)
class TrustScoreAggregationPolicy:
    def apply(self, contributions: tuple[float, ...]) -> float:
        return max(0.0, min(sum(contributions), 1.0))
