from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar

from rating_weighted.domain.value_objects.configuration import (
    BehaviorPenaltyConfig,
    MarkPenaltyConfig,
    TemporalConfig,
    TextPenaltyConfig,
)
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


@dataclass(frozen=True)
class BehaviourPenaltyPolicy:
    config: TemporalConfig
    penalty_config: BehaviorPenaltyConfig

    def apply(self, context: FeedbackMarkContext) -> float:
        number_of_reviews_left_in_24h = context.feedback.reviewer.activity.number_of_reviews_left_in_24h
        has_flag = context.feedback.moderation.has_flag
        last_repeat = context.feedback.timing.last_repeat
        now = context.now
        penalty = 0.0

        if self._is_repeated_feedback(last_repeat, now):
            penalty += self.penalty_config.penalty_feedback_repeat

        if self._is_burst(number_of_reviews_left_in_24h):
            penalty += self.penalty_config.penalty_burst

        if self._is_flagged(has_flag):
            penalty += self.penalty_config.penalty_flag

        return penalty

    def _is_repeated_feedback(self, last_repeat: datetime, now: datetime) -> bool:
        period = self.config.period_for_repeated_feedback_days

        return bool(now - last_repeat < timedelta(days=period))

    def _is_burst(self, number_of_reviews_left_in_24h: int) -> bool:
        return bool(number_of_reviews_left_in_24h > self.config.activity_surge_threshold_24h)

    def _is_flagged(self, has_flag: bool) -> bool:
        return bool(has_flag)


@dataclass(frozen=True)
class MarkPenaltyPolicy:
    _EXTREME_MARKS: ClassVar[tuple[int, int]] = (1, 10)

    config: MarkPenaltyConfig

    def apply(self, context: FeedbackMarkContext) -> float:
        should_apply = self._is_extreme_mark(context.mark.value) and self._is_short_or_empty_text(
            context.feedback.content.text
        )

        return self.config.penalty_text_extreme if should_apply else 0.0

    def _is_extreme_mark(self, mark: float) -> bool:
        return mark in self._EXTREME_MARKS

    def _is_short_or_empty_text(self, text: str | None) -> bool:
        if text is None:
            return True

        return len(text) < self.config.text_length_thresholds.short


@dataclass(frozen=True)
class TextPenaltyPolicy:
    config: TextPenaltyConfig

    def apply(self, context: FeedbackMarkContext) -> float:
        text = context.feedback.content.text
        moderation = context.feedback.moderation

        penalty = self._length_penalty(text)

        if moderation.text_has_template:
            penalty += self.config.penalty_text_template

        return penalty

    def _length_penalty(self, text: str | None) -> float:
        if text is None:
            return self.config.penalty_text_empty

        length = len(text)
        text_length_thresholds = self.config.text_length_thresholds

        if length < text_length_thresholds.short:
            return self.config.penalty_text_short

        if length < text_length_thresholds.long:
            return self.config.penalty_text_middle

        return self.config.penalty_text_long
