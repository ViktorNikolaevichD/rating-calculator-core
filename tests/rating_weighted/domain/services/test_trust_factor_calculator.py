from math import log

import pytest

from rating_weighted.domain.policies.trust_factors import (
    AccountAgeFactorPolicy,
    AccountVerificationFactorPolicy,
    ActivityDiversityFactorPolicy,
    FeedbackExperienceFactorPolicy,
    LongTermAccountRiskFactorPolicy,
    UsefulnessFactorPolicy,
)
from rating_weighted.domain.policies.trust_score_aggregation import TrustScoreAggregationPolicy
from rating_weighted.domain.services.trust_factor_calculator import TrustFactorCalculator
from rating_weighted.domain.value_objects.configuration import TemporalConfig
from tests.rating_weighted.domain.policies.helpers import make_rating_reviewer


@pytest.fixture
def trust_factor_calculator() -> TrustFactorCalculator:
    return TrustFactorCalculator(
        account_age_factor_policy=AccountAgeFactorPolicy(coefficient=0.30, max_days_for_full_score=30),
        feedback_experience_factor_policy=FeedbackExperienceFactorPolicy(coefficient=0.25),
        usefulness_factor_policy=UsefulnessFactorPolicy(coefficient=0.20),
        account_verification_factor_policy=AccountVerificationFactorPolicy(coefficient=0.15),
        activity_diversity_factor_policy=ActivityDiversityFactorPolicy(
            coefficient=0.10, max_unique_targets_for_full_score=10
        ),
        long_term_account_risk_factor_policy=LongTermAccountRiskFactorPolicy(
            config=TemporalConfig(
                period_for_repeated_feedback_days=7,
                activity_surge_threshold_24h=10,
                deleted_reviews_limit_for_period=3,
            ),
            coefficient=-0.25,
        ),
        trust_score_aggregation_policy=TrustScoreAggregationPolicy(),
    )


def test_calculate_returns_expected_weighted_sum_for_reviewer_without_risk(
    trust_factor_calculator: TrustFactorCalculator,
) -> None:
    reviewer = make_rating_reviewer(
        is_verified=True,
        has_flag=False,
        days_since_registration=15,
        unique_targets=5,
        approved_reviews=3,
        deleted_reviews_history_in_30d=0,
        received_likes_on_feedbacks=2,
        received_dislikes_on_feedbacks=1,
    )

    result = trust_factor_calculator.calculate(reviewer)

    expected = (
        0.30 * 0.5
        + 0.25 * (log(1 + 3) / log(1 + 20))
        + 0.20 * ((2 + 1) / (2 + 1 + 2))
        + 0.15 * 1.0
        + 0.10 * 0.5
        - 0.25 * 0.0
    )

    assert result == pytest.approx(expected), "Должна применяться формула Tu с вычитанием risk-фактора"


def test_calculate_returns_zero_when_negative_sum_goes_below_lower_bound(
    trust_factor_calculator: TrustFactorCalculator,
) -> None:
    reviewer = make_rating_reviewer(
        is_verified=False,
        has_flag=True,
        days_since_registration=0,
        unique_targets=0,
        approved_reviews=0,
        deleted_reviews_history_in_30d=10,
        received_likes_on_feedbacks=0,
        received_dislikes_on_feedbacks=0,
    )

    result = trust_factor_calculator.calculate(reviewer)

    assert result == 0.0, "Итоговый trust score должен быть ограничен снизу нулем"


def test_calculate_returns_one_when_sum_exceeds_upper_bound(
    trust_factor_calculator: TrustFactorCalculator,
) -> None:
    reviewer = make_rating_reviewer(
        is_verified=True,
        has_flag=False,
        days_since_registration=365,
        unique_targets=50,
        approved_reviews=10_000,
        deleted_reviews_history_in_30d=0,
        received_likes_on_feedbacks=1_000,
        received_dislikes_on_feedbacks=0,
    )

    result = trust_factor_calculator.calculate(reviewer)

    expected = (
        0.30 * 1.0
        + 0.25 * 1.0
        + 0.20 * ((1_000 + 1) / (1_000 + 0 + 2))
        + 0.15 * 1.0
        + 0.10 * 1.0
        - 0.25 * 0.0
    )

    assert result == pytest.approx(expected)
    assert result <= 1.0, "Итоговый trust score должен быть ограничен сверху единицей"
