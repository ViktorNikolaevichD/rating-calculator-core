from abc import abstractmethod

from rating_calculator_core.avg_rating.enums import NatureOfFeedbacks
from rating_calculator_core.avg_rating.dtos import PublishedOrganizationFeedbackWithMarksDTO
from rating_calculator_core.settings.services import Service


class OrganizationAvgRatingCalculator(Service):
    @abstractmethod
    def recalculate_organization_nature_of_feedbacks(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
    ) -> NatureOfFeedbacks | None:
        ...

    @abstractmethod
    def recalculate_organization_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
    ) -> int:
        ...

    @abstractmethod
    def recalculate_organization_category_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
        category_id: int,
    ) -> int:
        ...

    @abstractmethod
    def recalculate_organization_server_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
        server_id: int,
    ) -> int:
        ...

    @abstractmethod
    def recalculate_organization_participiant_avg_rating(
        self,
        organization_feedbacks_with_marks: list[PublishedOrganizationFeedbackWithMarksDTO],
        category_id: int,
        server_id: int,
    ) -> int:
        ...
