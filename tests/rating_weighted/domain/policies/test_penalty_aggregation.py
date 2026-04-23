from rating_weighted.domain.policies.penalty_aggregation import PenaltyAggregationPolicy
from rating_weighted.domain.value_objects.configuration import AggregatedPenaltyConfig


def test_apply_returns_sum_of_penalties_when_sum_is_below_max_total() -> None:
    config = AggregatedPenaltyConfig(maximum_total_feedback_penalty=2.0)
    policy = PenaltyAggregationPolicy(config=config)

    result = policy.apply([0.4, 0.3, 0.2])

    assert result == 0.9, "Сумма штрафов должна быть равна 0.9"


def test_apply_returns_max_total_when_sum_of_penalties_exceeds_cap() -> None:
    config = AggregatedPenaltyConfig(maximum_total_feedback_penalty=1.0)
    policy = PenaltyAggregationPolicy(config=config)

    result = policy.apply([0.6, 0.5, 0.4])

    assert result == config.maximum_total_feedback_penalty, "Сумма штрафов не должна превышать максимальное значение"
