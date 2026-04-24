from dataclasses import dataclass


@dataclass(frozen=True)
class FinalRatingCalculationResult:
    final_rating: float
    rating_maturity: float
