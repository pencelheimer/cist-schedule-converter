from typing import override

from pydantic import BaseModel, computed_field

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
    groups: list[Group] | None = []
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
        sp_grouops = {
            group
            for faculty in self.faculties
            for direction in faculty.directions
            for speciality in direction.specialities
            for group in speciality.groups
        }

        groups = {
            group
            for faculty in self.faculties
            for direction in faculty.directions
            for group in direction.groups or []
        }
        return groups | sp_grouops

class CistScheduleResponse(BaseModel):
    university: University
