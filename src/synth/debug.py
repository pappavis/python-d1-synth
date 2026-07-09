from dataclasses import dataclass
from enum import Enum


class DebugLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    VERBOSE = "verbose"


@dataclass(frozen=True)
class DebugReporter:
    level: DebugLevel

    def light(self, message: str) -> None:
        if self.level in {DebugLevel.LIGHT, DebugLevel.VERBOSE}:
            print(message)

    def verbose(self, message: str) -> None:
        if self.level is DebugLevel.VERBOSE:
            print(message)

