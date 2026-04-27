from datetime import datetime, timedelta

import pytest

from rating_kernel.domain.value_objects.feedback import (
    Feedback,
    FeedbackContent,
    FeedbackMark,
    FeedbackModerationState,
    FeedbackTimingContext,
)
from rating_kernel.domain.value_objects.reviewer import (
    Reviewer,
    ReviewerActivityProfile,
    ReviewerIdentity,
    ReviewerReputationHistory,
)
from rating_weighted.domain.policies.final_rating_aggregation import (
    BaseRatingContributionPolicy,
    ReviewerTrustContributionPolicy,
)
from rating_weighted.domain.policies.mark_score_aggregation import (
    AverageMarkWeightAggregationPolicy,
    TotalMarkWeightAggregationPolicy,
)
from rating_weighted.domain.policies.mark_weight_aggregation import MarkWeightAggregationPolicy
from rating_weighted.domain.services.mark_weight_calculator import MarkWeightCalculator
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
from rating_weighted.domain.value_objects.rating_context import RatingContext


class _StubTrustFactorCalculator:
    def __init__(self, trust_score: float) -> None:
        self.trust_score = trust_score
        self.calls_count = 0

    def calculate(self, reviewer: Reviewer) -> float:  # noqa: ARG002
        self.calls_count += 1
        return self.trust_score


class _StubPenaltyCalculator:
    def __init__(self, penalties_by_mark: dict[float, float]) -> None:
        self.penalties_by_mark = penalties_by_mark

    def calculate(self, context) -> float:
        return self.penalties_by_mark[context.mark.value]


def test_calculate_builds_feedback_with_weighted_marks() -> None:
    trust_calculator = _StubTrustFactorCalculator(trust_score=0.4)
    penalty_calculator = _StubPenaltyCalculator(
        penalties_by_mark={
            2.0: 0.10,
            8.0: 0.20,
        }
    )
    service = MarkWeightCalculator(
        trust_factor_calculator=trust_calculator,
        penalty_calculator=penalty_calculator,
        mark_weight_aggregation_policy=MarkWeightAggregationPolicy(
            config=FeedbackWeightAggregationConfig(
                range_of_final_mark_weight=RangeOfFinalMarkWeight(min=0.2, max=1.5)
            )
        ),
        total_mark_weight_aggregation_policy=TotalMarkWeightAggregationPolicy(),
        average_mark_weight_aggregation_policy=AverageMarkWeightAggregationPolicy(),
        base_rating_contribution_policy=BaseRatingContributionPolicy(
            config=WeightedRatingBaseConfig(base_rating=5.0, weight_division_coefficient=4)
        ),
        reviewer_trust_contribution_policy=ReviewerTrustContributionPolicy(
            config=WeightedRatingBaseConfig(base_rating=5.0, weight_division_coefficient=4)
        ),
    )
    context = _make_rating_context(mark_values=(2.0, 8.0))

    result = service.calculate(context)

    expected_w1 = (0.5 + 0.4) * (1 - 0.10)
    expected_w2 = (0.5 + 0.4) * (1 - 0.20)
    expected_feedback_weight = (expected_w1 + expected_w2) / 2

    assert trust_calculator.calls_count == 1
    assert result.feedback.content.marks[0].weight == pytest.approx(expected_w1)
    assert result.feedback.content.marks[1].weight == pytest.approx(expected_w2)
    assert result.feedback.weight == pytest.approx(expected_feedback_weight)
    assert result.feedback.trust_in_author == pytest.approx(0.4)
    assert result.now == context.now


def test_from_configuration_builds_service_with_required_dependencies() -> None:
    configuration = WeightedRatingConfiguration(
        base=WeightedRatingBaseConfig(base_rating=5.0, weight_division_coefficient=4),
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

    service = MarkWeightCalculator.from_configuration(configuration)

    assert service.mark_weight_aggregation_policy.config == configuration.feedback_weight_aggregation
    assert isinstance(service.average_mark_weight_aggregation_policy, AverageMarkWeightAggregationPolicy)
    assert service.base_rating_contribution_policy.config == configuration.base
    assert service.reviewer_trust_contribution_policy.config == configuration.base


def _make_rating_context(mark_values: tuple[float, ...]) -> RatingContext:
    now = datetime(2026, 4, 24, 12, 0, 0)
    reviewer = Reviewer(
        identity=ReviewerIdentity(is_verified=True, has_flag=False),
        activity=ReviewerActivityProfile(
            days_since_registration=100,
            number_of_reviews_left_in_24h=1,
            unique_targets=20,
        ),
        reputation=ReviewerReputationHistory(
            approved_reviews=50,
            deleted_reviews_history_in_30d=0,
            received_likes_on_feedbacks=10,
            received_dislikes_on_feedbacks=1,
        ),
    )
    feedback = Feedback(
        content=FeedbackContent(
            marks=tuple(FeedbackMark(value=value) for value in mark_values),
            text="weighted mark test text",
        ),
        moderation=FeedbackModerationState(text_has_template=False, has_flag=False),
        timing=FeedbackTimingContext(last_repeat=now - timedelta(days=30)),
        reviewer=reviewer,
    )

    return RatingContext(feedback=feedback, now=now)
