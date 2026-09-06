from pydantic import BaseModel, ConfigDict

from app.domain.games import Capability, GameDefinition, GameStatus


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    display_name: str
    category: str
    status: GameStatus
    capabilities: list[Capability]

    @classmethod
    def from_definition(cls, game: GameDefinition) -> "GameResponse":
        return cls(
            slug=game.slug,
            display_name=game.display_name,
            category=game.category,
            status=game.status,
            capabilities=sorted(game.capabilities, key=str),
        )


class CapabilityErrorResponse(BaseModel):
    game: str
    capability: str
    status: str
    message: str
