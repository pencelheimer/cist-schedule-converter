from typing import Annotated, Self, override
from pydantic import BaseModel, BeforeValidator, computed_field

class Group(BaseModel):
    id: int
    name: str

    @override
    def __hash__(self) -> int:
        return hash(self.id)

class Speciality(BaseModel):
    id: int
    short_name: str
    full_name: str
    groups: list[Group]

class Direction(BaseModel):
    id: int
    short_name: str
    full_name: str
    specialities: list[Speciality]

class Faculty(BaseModel):
    id: int
    short_name: str
    full_name: str
    directions: list[Direction]

class University(BaseModel):
    short_name: str
    full_name: str
    faculties: list[Faculty]

    @computed_field
    @property
    def groups(self) -> set[Group]:
        return {
            group
            for faculty in self.faculties
            for direction in faculty.directions
            for speciality in direction.specialities
            for group in speciality.groups
        }

class CistScheduleResponse(BaseModel):
    university: University

class EventDescription(BaseModel):
    subject: str
    event_type: str

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.subject == other.subject and self.event_type == other.event_type

    @override
    def __hash__(self) -> int:
        return hash((self.subject, self.event_type))

    @classmethod
    def from_cist_csv_topic(cls, raw: str) -> Self:
        parts = raw.strip().split(" ")
        subject = parts[0].replace("*", "").strip() if len(parts) > 0 else ""
        event_type = parts[1].strip() if len(parts) > 1 else ""
        return cls(subject=subject, event_type=event_type)

    @classmethod
    def from_query(cls, raw: str) -> Self:
        parts = raw.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid format '{raw}', expected 'subject:event_type'")
        return cls(subject=parts[0].strip(), event_type=parts[1].strip())

EventDescriptionFromQuery = Annotated[EventDescription, BeforeValidator(EventDescription.from_query)]

class MeetingUrl(BaseModel):
    subject: str
    event_type: str
    url_type: str
    url_id: str

    @computed_field
    @property
    def url(self) -> str:
        match self.url_type:
            case "google-meet":
                base = "https://meet.google.com/"
            case _:
                base = ""
        return f"{base}{self.url_id}"

    @classmethod
    def from_query(cls, raw: str) -> Self:
        parts = raw.split(":")
        if len(parts) != 4:
            raise ValueError(f"Invalid format '{raw}', expected 'subject:event_type:url_type:url_id'")
        return cls(
            subject=parts[0].strip(),
            event_type=parts[1].strip(),
            url_type=parts[2].strip(),
            url_id=parts[3].strip(),
        )

MeetingUrlFromQuery = Annotated[MeetingUrl, BeforeValidator(MeetingUrl.from_query)]
