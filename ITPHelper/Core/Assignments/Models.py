from enum import Enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class Assignment:

    class Status(Enum):
        RUNNING = 0
        CLOSED = 1

    id: str
    name: str
    status: Status

    has_reference: bool
    reference_id: Optional[str]

    has_testgen: bool
    testgen_id: Optional[str]

    @staticmethod
    def from_dict(data: dict) -> "Assignment":
        data_copy = data.copy()
        match data["status"]:
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
