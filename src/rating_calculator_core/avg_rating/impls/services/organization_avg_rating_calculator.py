from decimal import Decimal

from rating_calculator_core.avg_rating.dtos import PublishedOrganizationFeedbackWithMarksDTO
from rating_calculator_core.avg_rating.enums import OrganizationFeedbackNatureOfFeedback
from rating_calculator_core.avg_rating.services import OrganizationAvgRatingCalculator
from rating_calculator_core.avg_rating.enums import NatureOfFeedbacks


class OrganizationAvgRatingCalculatorImpl(OrganizationAvgRatingCalculator):
    def recalculate_organization_nature_of_feedbacks(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
    ) -> str | None:
        feedback_natures: list[OrganizationFeedbackNatureOfFeedback] = [
            OrganizationFeedbackNatureOfFeedback(feedback.nature_of_feedback)
            for feedback in organization_feedbacks_with_marks
        ]
        if len(feedback_natures) == 0:
            return None

        positive_feedback_percentage: Decimal = (
            self.__calculate_positive_feedback_percentage(
                feedback_natures=feedback_natures,
            )
        )
        if positive_feedback_percentage <= Decimal(20):
            return NatureOfFeedbacks.NEGATIVE.value
        if positive_feedback_percentage <= Decimal(40):
            return NatureOfFeedbacks.MOSTLY_NEGATIVE.value
        if positive_feedback_percentage <= Decimal(60):
            return NatureOfFeedbacks.MIXED.value
        if positive_feedback_percentage <= Decimal(80):
            return NatureOfFeedbacks.MOSTLY_POSITIVE.value
        return NatureOfFeedbacks.POSITIVE.value

    def recalculate_organization_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
    ) -> int:
        marks: list[int] = [
            mark
            for organization_feedback in organization_feedbacks_with_marks
            for mark in organization_feedback.marks
        ]
        return self.__calculate_avg_rating(marks=marks)
    
    def recalculate_organization_category_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
        category_id: int,
    ) -> int:
        marks: list[int] = [
            mark
            for organization_feedback in organization_feedbacks_with_marks
            if organization_feedback.category_id == category_id
            for mark in organization_feedback.marks
        ]
        return self.__calculate_avg_rating(marks=marks)

    def recalculate_organization_server_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
        server_id: int,
    ) -> int:
        marks: list[int] = [
            mark
            for organization_feedback in organization_feedbacks_with_marks
            if organization_feedback.server_id == server_id
            for mark in organization_feedback.marks
        ]
        return self.__calculate_avg_rating(marks=marks)

    def recalculate_organization_participiant_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
        category_id: int,
        server_id: int,
    ) -> int:
        marks: list[int] = [
            mark
            for organization_feedback in organization_feedbacks_with_marks
            if (
                organization_feedback.category_id == category_id
                and organization_feedback.server_id == server_id
            )
            for mark in organization_feedback.marks
        ]
        return self.__calculate_avg_rating(marks=marks)

    def __calculate_positive_feedback_percentage(
        self,
        feedback_natures: list[OrganizationFeedbackNatureOfFeedback],
    ) -> Decimal:
        positive_feedback_count: int = sum(
            1
            for feedback_nature in feedback_natures
            if feedback_nature is OrganizationFeedbackNatureOfFeedback.POSITIVE
        )
        return (Decimal(positive_feedback_count) * Decimal(100)) / Decimal(len(feedback_natures))

    def __calculate_avg_rating(
        self,
        marks: list[int],
    ) -> int:
        if len(marks) == 0:
            return 0

        average_mark: Decimal = Decimal(sum(marks)) / Decimal(len(marks))
        avg_rating: int = int(average_mark)
        return max(0, min(1000, avg_rating))
