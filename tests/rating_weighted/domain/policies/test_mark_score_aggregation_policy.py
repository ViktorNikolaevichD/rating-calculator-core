import pytest

from rating_kernel.domain.exceptions import ZeroTotalMarkWeightError
from rating_kernel.domain.value_objects.feedback import FeedbackMarkWithWeight
from rating_weighted.domain.policies.mark_score_aggregation import (
    TotalMarkWeightAggregationPolicy,
    WeightedAverageMarkScoreAggregationPolicy,
    AverageMarkWeightAggregationPolicy,
)


@pytest.fixture
def total_mark_weight_aggregation_policy() -> TotalMarkWeightAggregationPolicy:
    return TotalMarkWeightAggregationPolicy()


@pytest.fixture
def weighted_average_mark_score_aggregation_policy() -> WeightedAverageMarkScoreAggregationPolicy:
    return WeightedAverageMarkScoreAggregationPolicy()


def test_total_mark_weight_aggregation_policy_returns_sum_of_mark_weights(
    total_mark_weight_aggregation_policy: TotalMarkWeightAggregationPolicy,
) -> None:
    result = total_mark_weight_aggregation_policy.apply(
        (
            FeedbackMarkWithWeight(value=5.0, weight=0.6),
            FeedbackMarkWithWeight(value=3.0, weight=0.9),
            FeedbackMarkWithWeight(value=4.0, weight=1.2),
        )
    )

    assert result == 2.7, "Суммарный вес W должен быть равен сумме всех wi"


def test_weighted_average_mark_score_aggregation_policy_returns_weighted_average(
    weighted_average_mark_score_aggregation_policy: WeightedAverageMarkScoreAggregationPolicy,
) -> None:
    result = weighted_average_mark_score_aggregation_policy.apply(
        (
            FeedbackMarkWithWeight(value=5.0, weight=0.5),
            FeedbackMarkWithWeight(value=3.0, weight=1.0),
            FeedbackMarkWithWeight(value=4.0, weight=1.5),
        )
    )

    assert round(result, 2) == 3.83, "Aw должен рассчитываться как сумма (si * wi), деленная на сумму wi"


def test_weighted_average_mark_score_aggregation_policy_raises_domain_error_when_total_weight_is_zero(
    weighted_average_mark_score_aggregation_policy: WeightedAverageMarkScoreAggregationPolicy,
) -> None:
    with pytest.raises(ZeroTotalMarkWeightError):
        weighted_average_mark_score_aggregation_policy.apply(
            (
                FeedbackMarkWithWeight(value=5.0, weight=0.0),
                FeedbackMarkWithWeight(value=2.0, weight=0.0),
            )
        )


def test_average_mark_weight_returns_arithmetic_mean() -> None:
    policy = AverageMarkWeightAggregationPolicy()
    marks_with_weights = (
        FeedbackMarkWithWeight(value=5.0, weight=0.5),
        FeedbackMarkWithWeight(value=4.0, weight=1.5),
        FeedbackMarkWithWeight(value=3.0, weight=1.0),
    )

    result = policy.apply(marks_with_weights)

    assert result == pytest.approx((0.5 + 1.5 + 1.0) / 3), "Должно возвращаться среднее арифметическое весов"


def test_average_mark_weight_raises_when_no_marks_provided() -> None:
    policy = AverageMarkWeightAggregationPolicy()

    with pytest.raises(ZeroTotalMarkWeightError):
        policy.apply(())
