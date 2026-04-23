import pytest

from rating_weighted.domain.policies.trust_score_aggregation import TrustScoreAggregationPolicy


@pytest.fixture
def trust_score_aggregation_policy() -> TrustScoreAggregationPolicy:
    return TrustScoreAggregationPolicy()


def test_apply_returns_sum_of_contributions_when_sum_is_within_range(
    trust_score_aggregation_policy: TrustScoreAggregationPolicy
) -> None:
    result = trust_score_aggregation_policy.apply((0.2, 0.3, 0.1))

    assert result == 0.6, "Сумма вкладов должна быть равна 0.6"


def test_apply_returns_one_when_sum_of_contributions_exceeds_upper_bound(
    trust_score_aggregation_policy: TrustScoreAggregationPolicy
) -> None:
    result = trust_score_aggregation_policy.apply((0.7, 0.5))

    assert result == 1.0, "Сумма вкладов не должна превышать верхнюю границу 1.0"


def test_apply_returns_zero_when_sum_of_contributions_is_below_lower_bound(
    trust_score_aggregation_policy: TrustScoreAggregationPolicy
) -> None:
    result = trust_score_aggregation_policy.apply((-0.6, 0.2, 0.1))

    assert result == 0.0, "Сумма вкладов не должна опускаться ниже нижней границы 0.0"
