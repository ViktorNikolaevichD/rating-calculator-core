from dataclasses import dataclass

from rating_weighted.domain.policies.penalties import (
    BehaviourPenaltyPolicy,
    MarkPenaltyPolicy,
    TextPenaltyPolicy,
)
from rating_weighted.domain.policies.penalty_aggregation import PenaltyAggregationPolicy
from rating_weighted.domain.value_objects.configuration import WeightedRatingConfiguration
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext


@dataclass(frozen=True)
class PenaltyCalculator:
    text_penalty_policy: TextPenaltyPolicy
    mark_penalty_policy: MarkPenaltyPolicy
    behaviour_penalty_policy: BehaviourPenaltyPolicy
    penalty_aggregation_policy: PenaltyAggregationPolicy

    @classmethod
    def from_configuration(
        cls,
        configuration: WeightedRatingConfiguration,
    ) -> "PenaltyCalculator":
        return cls(
            text_penalty_policy=TextPenaltyPolicy(config=configuration.text),
            mark_penalty_policy=MarkPenaltyPolicy(config=configuration.mark),
            behaviour_penalty_policy=BehaviourPenaltyPolicy(
                config=configuration.temporal,
                penalty_config=configuration.behavior,
            ),
            penalty_aggregation_policy=PenaltyAggregationPolicy(config=configuration.aggregated),
        )

    def calculate(self, context: FeedbackMarkContext) -> float:
        penalties = (
            self.text_penalty_policy.apply(context),
            self.mark_penalty_policy.apply(context),
            self.behaviour_penalty_policy.apply(context),
        )

        return self.penalty_aggregation_policy.apply(penalties)
