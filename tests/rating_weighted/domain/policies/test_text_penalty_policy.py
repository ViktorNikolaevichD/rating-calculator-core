import pytest

from rating_weighted.domain.policies.text import TextPenaltyPolicy
from rating_weighted.domain.value_objects.configuration import TextLengthThresholds, TextPenaltyConfig
from tests.rating_weighted.domain.policies.helpers import make_feedback_mark_context


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


def test_apply_returns_empty_text_penalty_when_text_is_none(
    text_penalty_policy: TextPenaltyPolicy
) -> None:
    context = make_feedback_mark_context(text=None)

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_empty, "Должен быть наложен штраф за пустой текст"


def test_apply_returns_short_text_penalty_when_text_is_shorter_than_short_threshold(
    text_penalty_policy: TextPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(text="short")

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_short, "Должен быть наложен штраф за короткий текст"


def test_apply_returns_middle_text_penalty_when_text_length_is_between_thresholds(
    text_penalty_policy: TextPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(text="x" * text_penalty_policy.config.text_length_thresholds.short)

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_middle, "Должен быть наложен штраф за текст средней длины"


def test_apply_returns_long_text_penalty_when_text_length_reaches_long_threshold(
    text_penalty_policy: TextPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(text="x" * text_penalty_policy.config.text_length_thresholds.long)

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_long, "Должен быть наложен штраф за текст длинной длины"


def test_apply_adds_template_penalty_to_length_penalty_when_text_has_template(
    text_penalty_policy: TextPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(
        text="x" * text_penalty_policy.config.text_length_thresholds.short,
        text_has_template=True,
    )

    result = text_penalty_policy.apply(context)

    assert result == text_penalty_policy.config.penalty_text_template + text_penalty_policy.config.penalty_text_middle, \
        "Должен быть наложен штраф за текст средней длины с шаблоном"
