from app.domain.games import Capability as C
from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition(
        "progol_media_semana", "Progol Media Semana", "pool", GameStatus.PLANNED, frozenset(C)
    )
)
