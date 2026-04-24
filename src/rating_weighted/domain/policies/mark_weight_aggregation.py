from dataclasses import dataclass

from rating_weighted.domain.value_objects.configuration import FeedbackWeightAggregationConfig


@dataclass(frozen=True)
class MarkWeightAggregationPolicy:
    config: FeedbackWeightAggregationConfig
    trust_score_bias: float = 0.5

    def apply(self, trust_score: float, total_penalty: float) -> float:
        min_weight = self.config.range_of_final_mark_weight.min
        max_weight = self.config.range_of_final_mark_weight.max

        weight = (self.trust_score_bias + trust_score) * (1 - total_penalty)

        return max(min_weight, min(weight, max_weight))
