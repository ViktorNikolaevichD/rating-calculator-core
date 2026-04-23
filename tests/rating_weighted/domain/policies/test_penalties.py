from datetime import timedelta

import pytest

from rating_weighted.domain.policies.penalties import (
    BehaviourPenaltyPolicy,
    MarkPenaltyPolicy,
    TextPenaltyPolicy,
)
from rating_weighted.domain.value_objects.configuration import (
    BehaviorPenaltyConfig,
    MarkPenaltyConfig,
    TemporalConfig,
    TextLengthThresholds,
    TextPenaltyConfig,
)
from tests.rating_weighted.domain.policies.helpers import make_feedback_mark_context


@pytest.fixture
def behaviour_penalty_policy() -> BehaviourPenaltyPolicy:
    return BehaviourPenaltyPolicy(
        config=TemporalConfig(
            period_for_repeated_feedback_days=7,
            activity_surge_threshold_24h=10,
            deleted_reviews_limit_for_period=3,
        ),
        penalty_config=BehaviorPenaltyConfig(
            penalty_feedback_repeat=0.6,
            penalty_burst=0.4,
            penalty_flag=0.5,
        ),
    )


@pytest.fixture
def mark_penalty_policy() -> MarkPenaltyPolicy:
    return MarkPenaltyPolicy(
        config=MarkPenaltyConfig(
            text_length_thresholds=TextLengthThresholds(short=10, long=30),
            penalty_text_extreme=0.8,
        )
    )


@pytest.fixture
def text_penalty_policy() -> TextPenaltyPolicy:
    return TextPenaltyPolicy(
        config=TextPenaltyConfig(
            text_length_thresholds=TextLengthThresholds(short=10, long=30),
            penalty_text_empty=0.9,
            penalty_text_short=0.7,
            penalty_text_middle=0.4,
            penalty_text_long=0.1,
            penalty_text_template=0.3,
        )
    )


def test_behaviour_apply_adds_repeat_penalty_when_feedback_was_repeated_within_repeat_period(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
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


def test_behaviour_apply_adds_burst_penalty_when_review_count_exceeds_activity_threshold(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(
        reviews_left_in_24h=behaviour_penalty_policy.config.activity_surge_threshold_24h + 1,
    )

    result = behaviour_penalty_policy.apply(context)

    assert result == behaviour_penalty_policy.penalty_config.penalty_burst, "Должен быть наложен штраф за превышение порога активности"


def test_behaviour_apply_adds_flag_penalty_when_feedback_has_moderation_flag(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(has_flag=True)

    result = behaviour_penalty_policy.apply(context)

    assert result == behaviour_penalty_policy.penalty_config.penalty_flag, "Должен быть наложен штраф за флаг модерации"


def test_behaviour_apply_adds_all_penalties_when_repeat_burst_and_flag_conditions_are_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
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


def test_behaviour_apply_adds_repeat_and_burst_penalties_when_flag_condition_is_not_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
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


def test_behaviour_apply_adds_burst_and_flag_penalties_when_repeat_condition_is_not_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
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


def test_behaviour_apply_returns_zero_when_no_penalty_conditions_are_met(
    behaviour_penalty_policy: BehaviourPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(has_flag=False, reviews_left_in_24h=0)

    result = behaviour_penalty_policy.apply(context)

    assert result == 0.0, "Штраф не должен быть наложен, если ни одно условие не выполнено"


def test_mark_apply_returns_penalty_for_extreme_mark_with_short_text(
    mark_penalty_policy: MarkPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(mark_value=1, text="short")

    result = mark_penalty_policy.apply(context)

    assert result == mark_penalty_policy.config.penalty_text_extreme, "Должен быть наложен штраф за экстремальную оценку"


def test_mark_apply_returns_zero_for_extreme_mark_with_long_text(
    mark_penalty_policy: MarkPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(mark_value=10, text="x" * mark_penalty_policy.config.text_length_thresholds.short)

    result = mark_penalty_policy.apply(context)

    assert result == 0.0, "Не должен быть наложен штраф за экстремальную оценку"


def test_mark_apply_returns_zero_for_non_extreme_mark_with_short_text(
    mark_penalty_policy: MarkPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(mark_value=7, text="short")

    result = mark_penalty_policy.apply(context)

    assert result == 0.0, "Не должен быть наложен штраф за неэкстремальную оценку"


def test_text_apply_returns_empty_text_penalty_when_text_is_none(
    text_penalty_policy: TextPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(text=None)

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_empty, "Должен быть наложен штраф за пустой текст"


def test_text_apply_returns_short_text_penalty_when_text_is_shorter_than_short_threshold(
    text_penalty_policy: TextPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(text="short")

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_short, "Должен быть наложен штраф за короткий текст"


def test_text_apply_returns_middle_text_penalty_when_text_length_is_between_thresholds(
    text_penalty_policy: TextPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(text="x" * text_penalty_policy.config.text_length_thresholds.short)

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_middle, "Должен быть наложен штраф за текст средней длины"


def test_text_apply_returns_long_text_penalty_when_text_length_reaches_long_threshold(
    text_penalty_policy: TextPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(text="x" * text_penalty_policy.config.text_length_thresholds.long)

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_long, "Должен быть наложен штраф за текст длинной длины"


def test_text_apply_adds_template_penalty_to_length_penalty_when_text_has_template(
    text_penalty_policy: TextPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(
        text="x" * text_penalty_policy.config.text_length_thresholds.short,
        text_has_template=True,
    )

    result = text_penalty_policy.apply(context)

    assert result == (
        text_penalty_policy.config.penalty_text_template + text_penalty_policy.config.penalty_text_middle
    ), "Должен быть наложен штраф за текст средней длины с шаблоном"
