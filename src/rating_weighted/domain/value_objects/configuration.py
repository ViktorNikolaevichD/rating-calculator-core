from dataclasses import dataclass


@dataclass(frozen=True)
class WeightedRatingBaseConfig:
    base_rating: float
    weight_division_coefficient: int


@dataclass(frozen=True)
class RatingFactorsConfig:
    account_age_factor_coefficient: float
    feedback_experience_factor_coefficient: float
    usefulness_factor_coefficient_of_past_feedback: float
    account_verification_factor_coefficient: float
    activity_diversity_factor_coefficient: float
    long_term_account_risk_factor_coefficient: float


@dataclass(frozen=True)
class TextLengthThresholds:
    short: int
    long: int


@dataclass(frozen=True)
class TextPenaltyConfig:
    text_length_thresholds: TextLengthThresholds
    penalty_text_empty: float
    penalty_text_short: float
    penalty_text_middle: float
    penalty_text_long: float
    penalty_text_template: float


@dataclass(frozen=True)
class MarkPenaltyConfig:
    text_length_thresholds: TextLengthThresholds
    penalty_text_extreme: float


@dataclass(frozen=True)
class BehaviorPenaltyConfig:
    penalty_feedback_repeat: float
    penalty_burst: float
    penalty_flag: float


@dataclass(frozen=True)
class TemporalConfig:
    period_for_repeated_feedback_days: int
    activity_surge_threshold_24h: int
    deleted_reviews_limit_for_period: int


@dataclass(frozen=True)
class AggregatedPenaltyConfig:
    maximum_total_feedback_penalty: float


@dataclass(frozen=True)
class RangeOfFinalMarkWeight:
    min: float
    max: float


@dataclass(frozen=True)
class FeedbackWeightAggregationConfig:
    range_of_final_mark_weight: RangeOfFinalMarkWeight


@dataclass(frozen=True)
class WeightedRatingConfiguration:
    base: WeightedRatingBaseConfig
    factors: RatingFactorsConfig
    text: TextPenaltyConfig
    mark: MarkPenaltyConfig
    behavior: BehaviorPenaltyConfig
    temporal: TemporalConfig
    aggregated: AggregatedPenaltyConfig
    feedback_weight_aggregation: FeedbackWeightAggregationConfig
