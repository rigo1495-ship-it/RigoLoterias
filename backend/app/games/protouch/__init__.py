from app.domain.games import Capability as C
from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition("protouch", "Protouch", "protouch", GameStatus.PLANNED, frozenset(C))
)
