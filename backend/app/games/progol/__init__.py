from app.domain.games import Capability as C
from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition("progol", "Progol", "pool", GameStatus.PLANNED, frozenset(C))
)
