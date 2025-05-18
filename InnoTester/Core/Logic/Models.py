from enum import Enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class Assignment:

    class Status(Enum):
        NOTCONFIGURED = -1
        RUNNING = 0
        CLOSED = 1

    id: str
    name: str
    status: Status

    has_reference: bool = False
    reference_id: Optional[str] = None

    has_testgen: bool = False
    testgen_id: Optional[str] = None

    
    def is_configured(self) -> bool:
        return self.status != self.Status.NOTCONFIGURED


    @staticmethod
    def from_dict(data: dict) -> "Assignment":
        data_copy = data.copy()
        match data["status"]:
            case "NOTCONFIGURED": data_copy["status"] = Assignment.Status.NOTCONFIGURED
            case "RUNNING": data_copy["status"] = Assignment.Status.RUNNING
            case "CLOSED": data_copy["status"] = Assignment.Status.CLOSED
        return Assignment(**data_copy)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.name,
            "has_reference": self.has_reference,
            "reference_id": self.reference_id,
            "has_testgen": self.has_testgen,
            "testgen_id": self.testgen_id
        }

    def __str__(self) -> str:
        status_emoji = None
        match self.status:
            case Assignment.Status.NOTCONFIGURED: status_emoji = "🛠"
            case Assignment.Status.RUNNING: status_emoji = "✅"
            case Assignment.Status.CLOSED: status_emoji = "🌙"
        return (
            fr"{status_emoji} {self.name}"
        )

    def to_list_with_id(self) -> str:
        status_emoji = None
        match self.status:
            case Assignment.Status.NOTCONFIGURED: status_emoji = "🛠"
            case Assignment.Status.RUNNING: status_emoji = "✅"
            case Assignment.Status.CLOSED: status_emoji = "🌙"
        return (
            fr"{status_emoji} \(`{self.id}`\) {self.name}"
        )

    
@dataclass
class CodeRecord:
    id: str
    assignment_id: str
    ext: str
    author: str

    @staticmethod
    def from_dict(data: dict) -> "CodeRecord":
        return CodeRecord(**data)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "ext": self.ext,
            "author": self.author
        }

class Reference(CodeRecord): pass
class TestGen(CodeRecord): pass
