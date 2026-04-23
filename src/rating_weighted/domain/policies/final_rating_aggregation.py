from dataclasses import dataclass
from math import exp

from rating_weighted.domain.value_objects.configuration import WeightedRatingBaseConfig


@dataclass(frozen=True)
class FinalRatingAggregationPolicy:
    def apply(self, base_rating_contribution: float, reviewer_trust_contribution: float) -> float:
        return base_rating_contribution + reviewer_trust_contribution


@dataclass(frozen=True)
class BaseRatingContributionPolicy:
    config: WeightedRatingBaseConfig

    def apply(self, total_mark_weight: float) -> float:
        return self.config.base_rating * exp(-(total_mark_weight / self.config.weight_division_coefficient))


@dataclass(frozen=True)
class ReviewerTrustContributionPolicy:
    config: WeightedRatingBaseConfig

    def apply(self, weighted_average_mark: float, total_mark_weight: float) -> float:
        return weighted_average_mark * (1 - exp(-(total_mark_weight / self.config.weight_division_coefficient)))
