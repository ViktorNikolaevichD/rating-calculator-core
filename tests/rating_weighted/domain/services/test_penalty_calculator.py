from datetime import datetime

import pytest

from rating_weighted.domain.policies.penalties import (
    BehaviourPenaltyPolicy,
    MarkPenaltyPolicy,
    TextPenaltyPolicy,
)
from rating_weighted.domain.policies.penalty_aggregation import PenaltyAggregationPolicy
from rating_weighted.domain.services.penalty_calculator import PenaltyCalculator
from rating_weighted.domain.value_objects.configuration import (
    AggregatedPenaltyConfig,
    BehaviorPenaltyConfig,
    MarkPenaltyConfig,
    TemporalConfig,
    TextLengthThresholds,
    TextPenaltyConfig,
)
from tests.rating_weighted.domain.policies.helpers import make_feedback_mark_context


@pytest.fixture
def penalty_calculator() -> PenaltyCalculator:
    return PenaltyCalculator(
        text_penalty_policy=TextPenaltyPolicy(
            config=TextPenaltyConfig(
                text_length_thresholds=TextLengthThresholds(short=10, long=50),
                penalty_text_empty=0.20,
                penalty_text_short=0.10,
                penalty_text_middle=0.03,
                penalty_text_long=0.0,
                penalty_text_template=0.15,
            )
        ),
        mark_penalty_policy=MarkPenaltyPolicy(
            config=MarkPenaltyConfig(
                text_length_thresholds=TextLengthThresholds(short=10, long=50),
                penalty_text_extreme=0.25,
            )
        ),
        behaviour_penalty_policy=BehaviourPenaltyPolicy(
            config=TemporalConfig(
                period_for_repeated_feedback_days=7,
                activity_surge_threshold_24h=10,
                deleted_reviews_limit_for_period=3,
            ),
            penalty_config=BehaviorPenaltyConfig(
                penalty_feedback_repeat=0.12,
                penalty_burst=0.07,
                penalty_flag=0.21,
            ),
        ),
        penalty_aggregation_policy=PenaltyAggregationPolicy(
            config=AggregatedPenaltyConfig(maximum_total_feedback_penalty=0.8),
        ),
    )


def test_calculate_returns_sum_of_penalties_when_total_is_below_cap(
    penalty_calculator: PenaltyCalculator,
) -> None:
    context = make_feedback_mark_context(
        mark_value=1,
        text="short",
        text_has_template=False,
        has_flag=False,
        reviews_left_in_24h=0,
        now=datetime(2026, 4, 24, 12, 0, 0),
        last_repeat=datetime(2026, 3, 24, 12, 0, 0),
    )

    result = penalty_calculator.calculate(context)

    expected = 0.10 + 0.25 + 0.0
    assert result == pytest.approx(expected), "Pi должен быть суммой штрафов, если сумма меньше cap"


def test_calculate_returns_cap_when_total_penalty_exceeds_maximum(
    penalty_calculator: PenaltyCalculator,
) -> None:
    context = make_feedback_mark_context(
        mark_value=10,
        text=None,
        text_has_template=True,
        has_flag=True,
        reviews_left_in_24h=100,
        now=datetime(2026, 4, 24, 12, 0, 0),
        last_repeat=datetime(2026, 4, 23, 12, 0, 0),
    )

    result = penalty_calculator.calculate(context)

    assert result == 0.8, "Pi должен быть ограничен сверху значением cap=0.8"


def test_calculate_returns_zero_when_no_penalty_conditions_match(
    penalty_calculator: PenaltyCalculator,
) -> None:
    context = make_feedback_mark_context(
        mark_value=5,
        text="this feedback text is deliberately very long and descriptive to avoid length penalties",
        text_has_template=False,
        has_flag=False,
        reviews_left_in_24h=1,
        now=datetime(2026, 4, 24, 12, 0, 0),
        last_repeat=datetime(2026, 3, 24, 12, 0, 0),
    )

    result = penalty_calculator.calculate(context)

    assert result == 0.0, "Pi должен быть нулевым, когда ни одно условие штрафа не выполнено"
