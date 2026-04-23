from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewerIdentity:
    is_verified: bool
    has_flag: bool


@dataclass(frozen=True)
class ReviewerActivityProfile:
    days_since_registration: int
    number_of_reviews_left_in_24h: int
    unique_targets: int


@dataclass(frozen=True)
class ReviewerReputationHistory:
    approved_reviews: int
    deleted_reviews_history_in_30d: int
    received_likes_on_feedbacks: int
    received_dislikes_on_feedbacks: int


@dataclass(frozen=True)
class Reviewer:
    identity: ReviewerIdentity
    activity: ReviewerActivityProfile
    reputation: ReviewerReputationHistory
