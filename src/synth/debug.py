from dataclasses import dataclass
from enum import Enum


class DebugLevel(str, Enum):
    """CLI debug output levels.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-016
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-016 Debuglevel
    - Version: 0.1.0
    """

    NONE = "none"
    LIGHT = "light"
    VERBOSE = "verbose"


@dataclass(frozen=True)
class DebugReporter:
    """Print CLI diagnostics according to the selected debug level.

    Traceability:
    - Chatlog: CHATOD-20260709-D1PY-MVP-001 / US-016
    - Backlog: Sprint 1 Kanban Backlog
    - Epic: EPIC-005 Configuratie En CLI
    - User Story: US-016 Debuglevel
    - Version: 0.1.0
    """

    level: DebugLevel

    def light(self, message: str) -> None:
        if self.level in {DebugLevel.LIGHT, DebugLevel.VERBOSE}:
            print(message)

    def verbose(self, message: str) -> None:
        if self.level is DebugLevel.VERBOSE:
            print(message)
