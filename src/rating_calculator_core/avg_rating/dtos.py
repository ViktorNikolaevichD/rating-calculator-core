from dataclasses import dataclass

from rating_calculator_core.avg_rating.enums import OrganizationFeedbackNatureOfFeedback


@dataclass(slots=True)
class PublishedOrganizationFeedbackWithMarksDTO:
    id: int
    organization_id: int
    server_id: int
    category_id: int
    nature_of_feedback: OrganizationFeedbackNatureOfFeedback
    marks: list[int]
