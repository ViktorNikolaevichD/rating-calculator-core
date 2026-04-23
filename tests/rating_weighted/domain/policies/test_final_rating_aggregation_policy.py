import pytest

from rating_weighted.domain.policies.final_rating_aggregation import (
    BaseRatingContributionPolicy,
    FinalRatingAggregationPolicy,
    ReviewerTrustContributionPolicy,
)
from rating_weighted.domain.value_objects.configuration import WeightedRatingBaseConfig


@pytest.fixture
def base_rating_contribution_policy() -> BaseRatingContributionPolicy:
    return BaseRatingContributionPolicy(
        config=WeightedRatingBaseConfig(
            base_rating=4.0,
            weight_division_coefficient=4,
        )
    )


@pytest.fixture
def reviewer_trust_contribution_policy() -> ReviewerTrustContributionPolicy:
    return ReviewerTrustContributionPolicy(
        config=WeightedRatingBaseConfig(
            base_rating=4.0,
            weight_division_coefficient=4,
        )
    )


@pytest.fixture
def final_rating_aggregation_policy() -> FinalRatingAggregationPolicy:
    return FinalRatingAggregationPolicy()


def test_base_rating_contribution_policy_applies_exponential_decay_by_total_weight(
    base_rating_contribution_policy: BaseRatingContributionPolicy
) -> None:
    result = base_rating_contribution_policy.apply(total_mark_weight=4.0)

    assert result == pytest.approx(1.4715177646857693), "Базовый вклад должен рассчитываться по формуле B * e^(-W/4)"


def test_reviewer_trust_contribution_policy_applies_complement_of_exponential_decay(
    reviewer_trust_contribution_policy: ReviewerTrustContributionPolicy
) -> None:
    result = reviewer_trust_contribution_policy.apply(weighted_average_mark=3.0, total_mark_weight=4.0)

    assert result == pytest.approx(1.896361676485673), "Вклад доверия должен рассчитываться по формуле Aw * (1 - e^(-W/4))"


def test_final_rating_aggregation_policy_sums_two_contributions() -> None:
    policy = FinalRatingAggregationPolicy()

    result = policy.apply(
        base_rating_contribution=1.4715177646857693,
        reviewer_trust_contribution=1.896361676485673,
    )

    assert result == pytest.approx(3.3678794411714423), "Итоговый рейтинг должен быть суммой двух вкладов"


def test_full_formula_can_be_composed_from_two_policies_and_one_aggregator(
    reviewer_trust_contribution_policy: ReviewerTrustContributionPolicy,
    final_rating_aggregation_policy: FinalRatingAggregationPolicy,
) -> None:
    base_rating_contribution = BaseRatingContributionPolicy(
        config=WeightedRatingBaseConfig(
            base_rating=2.0,
            weight_division_coefficient=4,
        )
    ).apply(total_mark_weight=4.0)
    reviewer_trust_contribution = reviewer_trust_contribution_policy.apply(
        weighted_average_mark=4.0,
        total_mark_weight=4.0,
    )

    result = final_rating_aggregation_policy.apply(
        base_rating_contribution=base_rating_contribution,
        reviewer_trust_contribution=reviewer_trust_contribution,
    )

    assert result == pytest.approx(3.2642411176571153), "Композиция политик должна соответствовать итоговой формуле рейтинга"
