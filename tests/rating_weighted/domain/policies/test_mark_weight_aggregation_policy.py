import pytest

from rating_weighted.domain.policies.mark_weight_aggregation import (
    MarkWeightAggregationPolicy,
)
from rating_weighted.domain.value_objects.configuration import (
    FeedbackWeightAggregationConfig,
    RangeOfFinalMarkWeight,
)


@pytest.fixture
def feedback_weight_aggregation_policy() -> MarkWeightAggregationPolicy:
    return MarkWeightAggregationPolicy(
        config=FeedbackWeightAggregationConfig(
            range_of_final_mark_weight=RangeOfFinalMarkWeight(
                min=0.2,
                max=1.5,
            ),
        ),
    )


def test_apply_returns_raw_weight_when_formula_result_is_within_bounds(
    feedback_weight_aggregation_policy: MarkWeightAggregationPolicy
) -> None:
    result = feedback_weight_aggregation_policy.apply(trust_score=0.7, total_penalty=0.2)

    assert result == 0.96, "Вес должен рассчитываться по формуле без clamp внутри допустимого диапазона"


def test_apply_returns_min_weight_when_formula_result_is_below_lower_bound(
    feedback_weight_aggregation_policy: MarkWeightAggregationPolicy
) -> None:
    result = feedback_weight_aggregation_policy.apply(trust_score=0.0, total_penalty=0.8)

    assert result == 0.2, "Вес не должен опускаться ниже нижней границы"


def test_apply_returns_max_weight_when_formula_result_exceeds_upper_bound(
    feedback_weight_aggregation_policy: MarkWeightAggregationPolicy
) -> None:
    result = feedback_weight_aggregation_policy.apply(trust_score=1.0, total_penalty=-0.1)

    assert result == 1.5, "Вес не должен превышать верхнюю границу"
