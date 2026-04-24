from dataclasses import dataclass

from rating_kernel.domain.value_objects.reviewer import Reviewer
from rating_weighted.domain.policies.trust_factors import (
    AccountAgeFactorPolicy,
    AccountVerificationFactorPolicy,
    ActivityDiversityFactorPolicy,
    FeedbackExperienceFactorPolicy,
    LongTermAccountRiskFactorPolicy,
    UsefulnessFactorPolicy,
)
from rating_weighted.domain.policies.trust_score_aggregation import TrustScoreAggregationPolicy
from rating_weighted.domain.value_objects.configuration import WeightedRatingConfiguration


@dataclass(frozen=True)
class TrustFactorCalculator:
    account_age_factor_policy: AccountAgeFactorPolicy
    feedback_experience_factor_policy: FeedbackExperienceFactorPolicy
    usefulness_factor_policy: UsefulnessFactorPolicy
    account_verification_factor_policy: AccountVerificationFactorPolicy
    activity_diversity_factor_policy: ActivityDiversityFactorPolicy
    long_term_account_risk_factor_policy: LongTermAccountRiskFactorPolicy
    trust_score_aggregation_policy: TrustScoreAggregationPolicy

    @classmethod
    def from_configuration(cls, configuration: WeightedRatingConfiguration) -> "TrustFactorCalculator":
        factors = configuration.factors

        return cls(
            account_age_factor_policy=AccountAgeFactorPolicy(
                coefficient=factors.account_age_factor_coefficient
            ),
            feedback_experience_factor_policy=FeedbackExperienceFactorPolicy(
                coefficient=factors.feedback_experience_factor_coefficient
            ),
            usefulness_factor_policy=UsefulnessFactorPolicy(
                coefficient=factors.usefulness_factor_coefficient_of_past_feedback
            ),
            account_verification_factor_policy=AccountVerificationFactorPolicy(
                coefficient=factors.account_verification_factor_coefficient
            ),
            activity_diversity_factor_policy=ActivityDiversityFactorPolicy(
                coefficient=factors.activity_diversity_factor_coefficient
            ),
            long_term_account_risk_factor_policy=LongTermAccountRiskFactorPolicy(
                config=configuration.temporal,
                coefficient=factors.long_term_account_risk_factor_coefficient,
            ),
            trust_score_aggregation_policy=TrustScoreAggregationPolicy(),
        )

    def calculate(self, reviewer: Reviewer) -> float:
        contributions = (
            self.account_age_factor_policy.contribution(reviewer),
            self.feedback_experience_factor_policy.contribution(reviewer),
            self.usefulness_factor_policy.contribution(reviewer),
            self.account_verification_factor_policy.contribution(reviewer),
            self.activity_diversity_factor_policy.contribution(reviewer),
            self.long_term_account_risk_factor_policy.contribution(reviewer),
        )

        return self.trust_score_aggregation_policy.apply(contributions)
