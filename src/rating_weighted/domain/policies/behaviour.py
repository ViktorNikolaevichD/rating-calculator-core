from dataclasses import dataclass
from datetime import datetime, timedelta

from rating_weighted.domain.value_objects.configuration import BehaviorPenaltyConfig, TemporalConfig
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

        return bool(
            now - last_repeat < timedelta(days=period)
        )

    def _is_burst(self, number_of_reviews_left_in_24h: int) -> bool:
        return bool(
            number_of_reviews_left_in_24h > self.config.activity_surge_threshold_24h
        )

    def _is_flagged(self, has_flag: bool) -> bool:
        return bool(has_flag)
