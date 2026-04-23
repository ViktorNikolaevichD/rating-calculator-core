from datetime import timedelta

import pytest

from rating_weighted.domain.policies.behaviour import BehaviourPenaltyPolicy
from rating_weighted.domain.value_objects.configuration import BehaviorPenaltyConfig, TemporalConfig
from tests.rating_weighted.domain.policies.helpers import make_feedback_mark_context


@pytest.fixture
def behaviour_penalty_policy() -> BehaviourPenaltyPolicy:
    return BehaviourPenaltyPolicy(
        config=TemporalConfig(
            period_for_repeated_feedback_days=7,
            activity_surge_threshold_24h=10,
        ),
        penalty_config=BehaviorPenaltyConfig(
            penalty_feedback_repeat=0.6,
            penalty_burst=0.4,
            penalty_flag=0.5,
        ),
    )


def test_apply_adds_repeat_penalty_when_feedback_was_repeated_within_repeat_period(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    base_context = make_feedback_mark_context()
    context = make_feedback_mark_context(
        now=base_context.now,
        last_repeat=base_context.now - timedelta(
            days=behaviour_penalty_policy.config.period_for_repeated_feedback_days - 1,
        ),
    )

    result = behaviour_penalty_policy.apply(context)

    assert result == behaviour_penalty_policy.penalty_config.penalty_feedback_repeat, "Должен быть наложен штраф за повторную оценку"


def test_apply_adds_burst_penalty_when_review_count_exceeds_activity_threshold(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(
        reviews_left_in_24h=behaviour_penalty_policy.config.activity_surge_threshold_24h + 1,
    )

    result = behaviour_penalty_policy.apply(context)

    assert result == behaviour_penalty_policy.penalty_config.penalty_burst, "Должен быть наложен штраф за превышение порога активности"


def test_apply_adds_flag_penalty_when_feedback_has_moderation_flag(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(has_flag=True)

    result = behaviour_penalty_policy.apply(context)

    assert result == behaviour_penalty_policy.penalty_config.penalty_flag, "Должен быть наложен штраф за флаг модерации"


def test_apply_adds_all_penalties_when_repeat_burst_and_flag_conditions_are_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(
        reviews_left_in_24h=behaviour_penalty_policy.config.activity_surge_threshold_24h + 1,
        has_flag=True,
        last_repeat=make_feedback_mark_context().now - timedelta(
            days=behaviour_penalty_policy.config.period_for_repeated_feedback_days - 1,
        ),
    )

    result = behaviour_penalty_policy.apply(context)

    assert result == (
        behaviour_penalty_policy.penalty_config.penalty_feedback_repeat
        + behaviour_penalty_policy.penalty_config.penalty_burst
        + behaviour_penalty_policy.penalty_config.penalty_flag
    ), "Должны быть наложены все штрафы одновременно"


def test_apply_adds_repeat_and_burst_penalties_when_flag_condition_is_not_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(
        reviews_left_in_24h=behaviour_penalty_policy.config.activity_surge_threshold_24h + 1,
        has_flag=False,
        last_repeat=make_feedback_mark_context().now - timedelta(
            days=behaviour_penalty_policy.config.period_for_repeated_feedback_days - 1,
        ),
    )

    result = behaviour_penalty_policy.apply(context)

    assert result == (
        behaviour_penalty_policy.penalty_config.penalty_feedback_repeat
        + behaviour_penalty_policy.penalty_config.penalty_burst
    ), "Должны быть наложены штрафы за повтор и всплеск активности"


def test_apply_adds_burst_and_flag_penalties_when_repeat_condition_is_not_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(
        reviews_left_in_24h=behaviour_penalty_policy.config.activity_surge_threshold_24h + 1,
        has_flag=True,
        last_repeat=make_feedback_mark_context().now - timedelta(
            days=behaviour_penalty_policy.config.period_for_repeated_feedback_days,
        ),
    )

    result = behaviour_penalty_policy.apply(context)

    assert result == (
        behaviour_penalty_policy.penalty_config.penalty_burst
        + behaviour_penalty_policy.penalty_config.penalty_flag
    ), "Должны быть наложены штрафы за всплеск активности и флаг модерации"


def test_apply_returns_zero_when_no_penalty_conditions_are_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(has_flag=False, reviews_left_in_24h=0)

    result = behaviour_penalty_policy.apply(context)

    assert result == 0.0, "Штраф не должен быть наложен, если ни одно условие не выполнено"
