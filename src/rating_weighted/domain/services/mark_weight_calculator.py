from dataclasses import dataclass

from rating_kernel.domain.value_objects.feedback import (
    FeedbackContentWithMarkWeights,
    FeedbackMarkWithWeight,
    FeedbackWithMarkWeights,
)
from rating_weighted.domain.policies.final_rating_aggregation import (
    BaseRatingContributionPolicy,
    ReviewerTrustContributionPolicy,
)
from rating_weighted.domain.policies.mark_weight_aggregation import MarkWeightAggregationPolicy
from rating_weighted.domain.policies.mark_score_aggregation import (
    AverageMarkWeightAggregationPolicy,
    TotalMarkWeightAggregationPolicy,
    WeightedAverageMarkScoreAggregationPolicy,
)
from rating_weighted.domain.services.penalty_calculator import PenaltyCalculator
from rating_weighted.domain.services.trust_factor_calculator import TrustFactorCalculator
from rating_weighted.domain.value_objects.configuration import WeightedRatingConfiguration
from rating_weighted.domain.value_objects.feedback_mark_context import FeedbackMarkContext
from rating_weighted.domain.value_objects.rating_context import (
    RatingContext,
    RatingContextWithMarkWeights,
)


@dataclass(frozen=True)
class MarkWeightCalculator:
    trust_factor_calculator: TrustFactorCalculator
    penalty_calculator: PenaltyCalculator

    mark_weight_aggregation_policy: MarkWeightAggregationPolicy
    total_mark_weight_aggregation_policy: TotalMarkWeightAggregationPolicy
    average_mark_weight_aggregation_policy: AverageMarkWeightAggregationPolicy
    base_rating_contribution_policy: BaseRatingContributionPolicy
    reviewer_trust_contribution_policy: ReviewerTrustContributionPolicy

    @classmethod
    def from_configuration(cls, configuration: WeightedRatingConfiguration) -> "MarkWeightCalculator":
        return cls(
            trust_factor_calculator=TrustFactorCalculator.from_configuration(configuration),
            penalty_calculator=PenaltyCalculator.from_configuration(configuration),
            mark_weight_aggregation_policy=MarkWeightAggregationPolicy(
                config=configuration.feedback_weight_aggregation
            ),
            total_mark_weight_aggregation_policy=TotalMarkWeightAggregationPolicy(),
            average_mark_weight_aggregation_policy=AverageMarkWeightAggregationPolicy(),
            base_rating_contribution_policy=BaseRatingContributionPolicy(config=configuration.base),
            reviewer_trust_contribution_policy=ReviewerTrustContributionPolicy(
                config=configuration.base
            ),
        )

    def calculate(self, context: RatingContext) -> RatingContextWithMarkWeights:
        trust_score = self.trust_factor_calculator.calculate(context.feedback.reviewer)
        marks_with_weights = tuple(
            self._build_mark_with_weight(mark_context, trust_score)
            for mark_context in context.per_mark_contexts()
        )

        weighted_average_mark: float = self.average_mark_weight_aggregation_policy.apply(
            marks_with_weights
        )

        feedback_with_mark_weights = self._build_feedback_with_mark_weights(
            context=context,
            weighted_average_mark=weighted_average_mark,
            marks_with_weights=marks_with_weights,
            trust_score=trust_score,
        )

        return RatingContextWithMarkWeights(
            feedback=feedback_with_mark_weights,
            now=context.now,
        )

    def _build_mark_with_weight(
        self,
        mark_context: FeedbackMarkContext,
        trust_score: float,
    ) -> FeedbackMarkWithWeight:
        total_penalty = self.penalty_calculator.calculate(mark_context)
        mark_weight = self.mark_weight_aggregation_policy.apply(
            trust_score=trust_score,
            total_penalty=total_penalty,
        )

        return FeedbackMarkWithWeight(
            value=mark_context.mark.value,
            weight=mark_weight,
        )

    def _build_feedback_with_mark_weights(
        self,
        context: RatingContext,
        weighted_average_mark: float,
        marks_with_weights: tuple[FeedbackMarkWithWeight, ...],
        trust_score: float,
    ) -> FeedbackWithMarkWeights:
        return FeedbackWithMarkWeights(
            content=FeedbackContentWithMarkWeights(
                marks=marks_with_weights,
                text=context.feedback.content.text,
            ),
            moderation=context.feedback.moderation,
            timing=context.feedback.timing,
            reviewer=context.feedback.reviewer,
            weight=weighted_average_mark,
            trust_in_author=trust_score,
        )
