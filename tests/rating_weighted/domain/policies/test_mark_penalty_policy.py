import pytest

from rating_weighted.domain.policies.mark import MarkPenaltyPolicy
from rating_weighted.domain.value_objects.configuration import MarkPenaltyConfig, TextLengthThresholds
from tests.rating_weighted.domain.policies.helpers import make_feedback_mark_context


@pytest.fixture
def mark_penalty_policy() -> MarkPenaltyPolicy:
    return MarkPenaltyPolicy(
        config=MarkPenaltyConfig(
            text_length_thresholds=TextLengthThresholds(short=10, long=30),
            penalty_text_extreme=0.8,
        )
    )


def test_apply_returns_penalty_for_extreme_mark_with_short_text(
    mark_penalty_policy: MarkPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(mark_value=1, text="short")

    result = mark_penalty_policy.apply(context)

    assert result == mark_penalty_policy.config.penalty_text_extreme, "Должен быть наложен штраф за экстремальную оценку"


def test_apply_returns_zero_for_extreme_mark_with_long_text(
    mark_penalty_policy: MarkPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(mark_value=10, text="x" * mark_penalty_policy.config.text_length_thresholds.short)

    result = mark_penalty_policy.apply(context)

    assert result == 0.0, "Не должен быть наложен штраф за экстремальную оценку"


def test_apply_returns_zero_for_non_extreme_mark_with_short_text(
    mark_penalty_policy: MarkPenaltyPolicy,
) -> None:
    context = make_feedback_mark_context(mark_value=7, text="short")

    result = mark_penalty_policy.apply(context)

    assert result == 0.0, "Не должен быть наложен штраф за неэкстремальную оценку"
