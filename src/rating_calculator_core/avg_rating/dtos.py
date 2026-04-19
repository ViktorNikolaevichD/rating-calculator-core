from dataclasses import dataclass


@dataclass(slots=True)
class PublishedOrganizationFeedbackWithMarksDTO:
    id: int
    organization_id: int
    server_id: int
    category_id: int
    nature_of_feedback: str
    marks: list[int]
