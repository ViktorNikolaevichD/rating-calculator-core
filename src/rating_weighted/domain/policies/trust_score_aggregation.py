from dataclasses import dataclass


@dataclass(frozen=True)
class TrustScoreAggregationPolicy:
    def apply(self, contributions: tuple[float, ...]) -> float:
        score = sum(contributions)

        return max(0.0, min(score, 1.0))
