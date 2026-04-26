import pytest

from rating_weighted.domain.policies.trust_factors import (
    AccountAgeFactorPolicy,
    AccountVerificationFactorPolicy,
    ActivityDiversityFactorPolicy,
    FeedbackExperienceFactorPolicy,
    LongTermAccountRiskFactorPolicy,
    UsefulnessFactorPolicy,
)
from rating_weighted.domain.value_objects.configuration import TemporalConfig
from tests.rating_weighted.domain.policies.helpers import make_rating_reviewer


@pytest.fixture
def account_age_factor_policy() -> AccountAgeFactorPolicy:
    return AccountAgeFactorPolicy(
        coefficient=0.30,
        max_days_for_full_score=30,
    )


@pytest.fixture
def feedback_experience_factor_policy() -> FeedbackExperienceFactorPolicy:
    return FeedbackExperienceFactorPolicy(
        coefficient=0.25,
    )


@pytest.fixture
def long_term_risk_policy() -> LongTermAccountRiskFactorPolicy:
    return LongTermAccountRiskFactorPolicy(
        config=TemporalConfig(
            period_for_repeated_feedback_days=7,
            activity_surge_threshold_24h=10,
            deleted_reviews_limit_for_period=3,
        ),
        coefficient=0.25,
    )


def test_account_age_factor_policy_returns_fraction_of_days_for_non_mature_account(
    account_age_factor_policy: AccountAgeFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(days_since_registration=15)

    result = account_age_factor_policy.apply(reviewer)

    assert result == 0.5, "Фактор возраста аккаунта должен быть пропорционален возрасту до достижения порога"


def test_account_age_factor_policy_is_capped_at_one_for_old_account(
    account_age_factor_policy: AccountAgeFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(days_since_registration=100)

    result = account_age_factor_policy.apply(reviewer)

    assert result == 1.0, "Фактор возраста аккаунта должен быть ограничен значением 1.0"


def test_account_age_factor_policy_contribution_applies_coefficient_to_factor(
    account_age_factor_policy: AccountAgeFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(days_since_registration=15)

    result = account_age_factor_policy.contribution(reviewer)

    assert result == 0.15, "Вклад фактора возраста должен учитывать коэффициент policy"


def test_feedback_experience_factor_policy_returns_zero_without_approved_reviews(
    feedback_experience_factor_policy: FeedbackExperienceFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(approved_reviews=0)

    result = feedback_experience_factor_policy.apply(reviewer)

    assert result == 0.0, "Фактор опыта должен быть нулевым при отсутствии одобренных отзывов"


def test_feedback_experience_factor_policy_is_capped_at_one_for_high_experience(
    feedback_experience_factor_policy: FeedbackExperienceFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(approved_reviews=1_000)

    result = feedback_experience_factor_policy.apply(reviewer)

    assert result == 1.0, "Фактор опыта должен быть ограничен значением 1.0"


def test_usefulness_factor_policy_applies_like_dislike_smoothing_formula() -> None:
    policy = UsefulnessFactorPolicy(coefficient=0.20)
    reviewer = make_rating_reviewer(
        received_likes_on_feedbacks=4,
        received_dislikes_on_feedbacks=6,
    )

    result = policy.apply(reviewer)

    expected = (4 + 1) / (4 + 6 + 2)

    assert result == expected, "Фактор полезности должен рассчитываться с учетом сглаживания (likes + 1) и делителем +2"


def test_account_verification_factor_policy_returns_one_for_verified_account() -> None:
    policy = AccountVerificationFactorPolicy(coefficient=0.15)
    reviewer = make_rating_reviewer(is_verified=True)

    result = policy.apply(reviewer)

    assert result == 1.0, "Подтвержденный аккаунт должен давать максимальный фактор верификации"


def test_account_verification_factor_policy_returns_zero_for_unverified_account() -> None:
    policy = AccountVerificationFactorPolicy(coefficient=0.15)
    reviewer = make_rating_reviewer(is_verified=False)

    result = policy.apply(reviewer)

    assert result == 0.0, "Неподтвержденный аккаунт должен давать нулевой фактор верификации"


def test_activity_diversity_factor_policy_returns_fraction_for_low_diversity() -> None:
    policy = ActivityDiversityFactorPolicy(coefficient=0.10, max_unique_targets_for_full_score=10)
    reviewer = make_rating_reviewer(unique_targets=4)

    result = policy.apply(reviewer)

    assert result == 0.4, "Фактор разнообразия должен быть пропорционален числу уникальных целей до порога"


def test_activity_diversity_factor_policy_is_capped_at_one_for_high_diversity() -> None:
    policy = ActivityDiversityFactorPolicy(coefficient=0.10, max_unique_targets_for_full_score=10)
    reviewer = make_rating_reviewer(unique_targets=50)

    result = policy.apply(reviewer)

    assert result == 1.0, "Фактор разнообразия должен быть ограничен значением 1.0"


def test_long_term_account_risk_factor_policy_returns_only_flag_ratio_when_only_flag_is_present(
    long_term_risk_policy: LongTermAccountRiskFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(has_flag=True, deleted_reviews_history_in_30d=0)

    result = long_term_risk_policy.apply(reviewer)

    assert result == long_term_risk_policy.account_flag_ratio, "Должен учитываться только риск-фактор флага аккаунта"


def test_long_term_account_risk_factor_policy_returns_only_deleted_reviews_ratio_when_limit_is_exceeded(
    long_term_risk_policy: LongTermAccountRiskFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(
        has_flag=False,
        deleted_reviews_history_in_30d=long_term_risk_policy.config.deleted_reviews_limit_for_period + 1,
    )

    result = long_term_risk_policy.apply(reviewer)

    assert result == long_term_risk_policy.deleted_reviews_history_ratio, "Должен учитываться только риск-фактор истории удалений"


def test_long_term_account_risk_factor_policy_returns_zero_when_no_risk_signals_are_present(
    long_term_risk_policy: LongTermAccountRiskFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(
        has_flag=False,
        deleted_reviews_history_in_30d=long_term_risk_policy.config.deleted_reviews_limit_for_period,
    )

    result = long_term_risk_policy.apply(reviewer)

    assert result == 0.0, "Риск-фактор должен быть нулевым, когда ни одно условие риска не выполнено"


def test_long_term_account_risk_factor_policy_sums_all_risks_when_all_signals_are_present(
    long_term_risk_policy: LongTermAccountRiskFactorPolicy
) -> None:
    reviewer = make_rating_reviewer(
        has_flag=True,
        deleted_reviews_history_in_30d=long_term_risk_policy.config.deleted_reviews_limit_for_period + 1,
    )

    result = long_term_risk_policy.apply(reviewer)

    assert result == (
        long_term_risk_policy.account_flag_ratio + long_term_risk_policy.deleted_reviews_history_ratio
    ), "Должны суммироваться оба долгосрочных риск-фактора"
