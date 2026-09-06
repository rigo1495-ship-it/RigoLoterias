from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityUnavailableError(Exception):
    game: str
    capability: str
    status: str
    message: str
