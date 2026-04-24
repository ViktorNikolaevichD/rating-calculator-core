from dataclasses import dataclass

from rating_kernel.domain.value_objects.feedback import FeedbackMarkWithWeight
from rating_weighted.domain.policies.final_rating_aggregation import (
    BaseRatingContributionPolicy,
    FinalRatingAggregationPolicy,
    ReviewerTrustContributionPolicy,
)
from rating_weighted.domain.policies.mark_score_aggregation import (
    TotalMarkWeightAggregationPolicy,
    WeightedAverageMarkScoreAggregationPolicy,
)
from rating_weighted.domain.value_objects.configuration import WeightedRatingBaseConfig


@dataclass(frozen=True)
class FinalRatingCalculator:
    total_mark_weight_aggregation_policy: TotalMarkWeightAggregationPolicy
    weighted_average_mark_score_aggregation_policy: WeightedAverageMarkScoreAggregationPolicy
    base_rating_contribution_policy: BaseRatingContributionPolicy
    reviewer_trust_contribution_policy: ReviewerTrustContributionPolicy
    final_rating_aggregation_policy: FinalRatingAggregationPolicy

    @classmethod
    def from_configuration(cls, configuration: WeightedRatingBaseConfig) -> "FinalRatingCalculator":
        return cls(
            total_mark_weight_aggregation_policy=TotalMarkWeightAggregationPolicy(),
            weighted_average_mark_score_aggregation_policy=WeightedAverageMarkScoreAggregationPolicy(),
            base_rating_contribution_policy=BaseRatingContributionPolicy(config=configuration),
            reviewer_trust_contribution_policy=ReviewerTrustContributionPolicy(
                config=configuration
            ),
            final_rating_aggregation_policy=FinalRatingAggregationPolicy(),
        )

    def calculate(self, marks_with_weights: tuple[FeedbackMarkWithWeight, ...]) -> float:
        total_mark_weight = self.total_mark_weight_aggregation_policy.apply(marks_with_weights)
        weighted_average_mark = self.weighted_average_mark_score_aggregation_policy.apply(
            marks_with_weights
        )
        base_rating_contribution = self.base_rating_contribution_policy.apply(
            total_mark_weight=total_mark_weight
        )
        reviewer_trust_contribution = self.reviewer_trust_contribution_policy.apply(
            weighted_average_mark=weighted_average_mark,
            total_mark_weight=total_mark_weight,
        )

        return self.final_rating_aggregation_policy.apply(
            base_rating_contribution=base_rating_contribution,
            reviewer_trust_contribution=reviewer_trust_contribution,
        )
