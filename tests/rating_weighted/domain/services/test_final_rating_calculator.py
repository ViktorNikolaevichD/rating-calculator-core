import pytest

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
from rating_weighted.domain.services.final_rating_calculator import FinalRatingCalculator
from rating_weighted.domain.value_objects.configuration import WeightedRatingBaseConfig


def test_calculate_returns_final_rating_from_marks_with_weights() -> None:
    service = FinalRatingCalculator(
        total_mark_weight_aggregation_policy=TotalMarkWeightAggregationPolicy(),
        weighted_average_mark_score_aggregation_policy=WeightedAverageMarkScoreAggregationPolicy(),
        base_rating_contribution_policy=BaseRatingContributionPolicy(
            config=WeightedRatingBaseConfig(base_rating=4.0, weight_division_coefficient=4)
        ),
        reviewer_trust_contribution_policy=ReviewerTrustContributionPolicy(
            config=WeightedRatingBaseConfig(base_rating=4.0, weight_division_coefficient=4)
        ),
        final_rating_aggregation_policy=FinalRatingAggregationPolicy(),
    )
    marks_with_weights = (
        FeedbackMarkWithWeight(value=5.0, weight=0.5),
        FeedbackMarkWithWeight(value=3.0, weight=1.0),
        FeedbackMarkWithWeight(value=4.0, weight=1.5),
    )

    result = service.calculate(marks_with_weights)

    assert result == pytest.approx(3.91206109), "Rfinal должен рассчитываться по формулам W, Aw и вкладов"


def test_from_configuration_builds_service_with_base_configuration() -> None:
    configuration = WeightedRatingBaseConfig(base_rating=4.0, weight_division_coefficient=4)

    service = FinalRatingCalculator.from_configuration(configuration)

    assert service.base_rating_contribution_policy.config == configuration
    assert service.reviewer_trust_contribution_policy.config == configuration
