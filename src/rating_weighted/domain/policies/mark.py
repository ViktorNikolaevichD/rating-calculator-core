from dataclasses import dataclass
from typing import ClassVar

from rating_weighted.domain.value_objects.configuration import MarkPenaltyConfig
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


@dataclass(frozen=True)
class MarkPenaltyPolicy:
    _EXTREME_MARKS: ClassVar[tuple[int, int]] = (1, 10)

    config: MarkPenaltyConfig

    def apply(self, context: FeedbackMarkContext) -> float:
        should_apply = (
            self._is_extreme_mark(context.mark.value)
            and self._is_short_or_empty_text(context.feedback.content.text)
        )

        return self.config.penalty_text_extreme if should_apply else 0.0

    def _is_extreme_mark(self, mark: float) -> bool:
        return mark in self._EXTREME_MARKS

    def _is_short_or_empty_text(self, text: str | None) -> bool:
        if text is None:
            return True

        return len(text) < self.config.text_length_thresholds.short
