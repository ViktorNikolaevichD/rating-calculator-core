from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class FinalRatingAggregationPolicy:
    def apply(self, base_rating_contribution: float, reviewer_trust_contribution: float) -> float:
        return base_rating_contribution + reviewer_trust_contribution


@dataclass(frozen=True)
class BaseRatingContributionPolicy:
    weight_decay_divisor: float = 4.0

    def apply(self, base_rating: float, total_mark_weight: float) -> float:
        return base_rating * exp(-(total_mark_weight / self.weight_decay_divisor))


@dataclass(frozen=True)
class ReviewerTrustContributionPolicy:
    weight_decay_divisor: float = 4.0

    def apply(self, weighted_average_mark: float, total_mark_weight: float) -> float:
        return weighted_average_mark * (1 - exp(-(total_mark_weight / self.weight_decay_divisor)))
