from dataclasses import dataclass


@dataclass(frozen=True)
class VersionInfo:
    major: int = 0
    minor: int = 1
    patch: int = 0

    def as_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

