from dataclasses import dataclass

from rating_weighted.domain.value_objects.configuration import TextPenaltyConfig
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


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
