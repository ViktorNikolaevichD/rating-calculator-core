from math import exp

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
from rating_weighted.domain.value_objects.configuration import (
    AggregatedPenaltyConfig,
    BehaviorPenaltyConfig,
    FeedbackWeightAggregationConfig,
    MarkPenaltyConfig,
    RangeOfFinalMarkWeight,
    RatingFactorsConfig,
    TemporalConfig,
    TextLengthThresholds,
    TextPenaltyConfig,
    WeightedRatingBaseConfig,
    WeightedRatingConfiguration,
)


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
    configuration = WeightedRatingConfiguration(
        base=WeightedRatingBaseConfig(base_rating=4.0, weight_division_coefficient=4),
        factors=RatingFactorsConfig(
            account_age_factor_coefficient=0.30,
            feedback_experience_factor_coefficient=0.25,
            usefulness_factor_coefficient_of_past_feedback=0.20,
            account_verification_factor_coefficient=0.15,
            activity_diversity_factor_coefficient=0.10,
            long_term_account_risk_factor_coefficient=0.25,
        ),
        text=TextPenaltyConfig(
            text_length_thresholds=TextLengthThresholds(short=10, long=50),
            penalty_text_empty=0.2,
            penalty_text_short=0.1,
            penalty_text_middle=0.03,
            penalty_text_long=0.0,
            penalty_text_template=0.15,
        ),
        mark=MarkPenaltyConfig(
            text_length_thresholds=TextLengthThresholds(short=10, long=50),
            penalty_text_extreme=0.25,
        ),
        behavior=BehaviorPenaltyConfig(
            penalty_feedback_repeat=0.12,
            penalty_burst=0.07,
            penalty_flag=0.21,
        ),
        temporal=TemporalConfig(
            period_for_repeated_feedback_days=7,
            activity_surge_threshold_24h=10,
            deleted_reviews_limit_for_period=3,
        ),
        aggregated=AggregatedPenaltyConfig(maximum_total_feedback_penalty=0.8),
        feedback_weight_aggregation=FeedbackWeightAggregationConfig(
            range_of_final_mark_weight=RangeOfFinalMarkWeight(min=0.2, max=1.5)
        ),
    )

    service = FinalRatingCalculator.from_configuration(configuration)

    assert service.base_rating_contribution_policy.config == configuration.base
    assert service.reviewer_trust_contribution_policy.config == configuration.base
