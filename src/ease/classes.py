from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, RootModel


class LocalizedText(RootModel[Dict[str, Optional[str]]]):
    pass


class Person(BaseModel):
    id: int
    currentFirstName: str
    currentLastName: str


class ActivityType(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None


class InterventionInstructor(BaseModel):
    id: int
    person: Person


class PedagogicalUnit(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None
    externalCode: Optional[Dict[str, Any]] = None
    customAttributes: Optional[Dict[str, Any]] = None


class Population(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None
    externalCode: Optional[Dict[str, Any]] = None
    populationType: Optional[Dict[str, Any]] = None


class Program(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None


class ResourceType(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None
    isManagingConflictsEnabled: Optional[bool] = None


class Resource(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None
    description: Optional[LocalizedText] = None
    floor: Optional[int] = None
    examCapacity: Optional[int] = None
    totalCapacity: Optional[int] = None
    isAccessibleForDisablePeople: Optional[bool] = None
    isRoom: Optional[bool] = None
    resourceType: Optional[ResourceType] = None


class AttendanceStatus(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None


class Participation(BaseModel):
    id: int
    absenceExcused: bool
    absenceReason: Optional[Dict[str, Any]] = None
    attendanceStatus: Optional[AttendanceStatus] = None
    automaticRegistrationStatus: Optional[AttendanceStatus] = None
    participationStatus: Optional[Dict[str, Any]] = None
    isRemote: bool
    person: Person


class Timezone(BaseModel):
    id: int
    abbreviation: Optional[str] = None
    code: str
    description: Optional[str] = None
    dst: Optional[bool] = None
    name: str
    utcOffset: Optional[float] = None
    utcOffsetWithDst: Optional[float] = None


class InterventionStatus(BaseModel):
    id: int
    code: str
    caption: Optional[LocalizedText] = None
    isAccessAttendanceListsDisabled: Optional[bool] = None
    isBillable: Optional[bool] = None
    isDisplayedInSchedules: Optional[bool] = None
    isHoursTaughtCountedInPrc: Optional[bool] = None
    isHoursTaughtCountedInWorkloadPlan: Optional[bool] = None
    isHoursTaughtExportedToPayroll: Optional[bool] = None
    isInstructorConflictsEnabled: Optional[bool] = None
    isLearnerConflictsEnabled: Optional[bool] = None
    isPartOfAttendanceLists: Optional[bool] = None
    isResourceConflictsEnabled: Optional[bool] = None
    toSchedule: Optional[bool] = None


class Intervention(BaseModel):
    id: int
    activityType: ActivityType
    actualDuration: int
    startDateTime: datetime
    endDateTime: datetime
    field: Optional[Dict[str, Any]] = None
    isExam: bool
    interventionInstructors: Optional[List[InterventionInstructor]] = None
    interventionPedagogicalUnits: Optional[List[Any]] = None
    interventionPopulations: Optional[List[Any]] = None
    interventionPrograms: Optional[List[Any]] = None
    interventionResources: Optional[List[Any]] = None
    interventionStatus: Optional[InterventionStatus] = None
    participations: Optional[List[Participation]] = None
    timezone: Optional[Timezone] = None


class InterventionsExport(BaseModel):
    interventions: List[Intervention]
    unavailabilities: List[Any]


def load_interventions_export(file_path: str) -> InterventionsExport:
    import json

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return InterventionsExport.model_validate(data)


def load_interventions(json_txt: str) -> InterventionsExport:
    import json

    return InterventionsExport.model_validate(json_txt)
