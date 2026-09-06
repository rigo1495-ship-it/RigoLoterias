from app.domain.games import Capability as C
from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition(
        "progol_media_semana",
        "Progol Media Semana",
        "pool",
        GameStatus.AVAILABLE,
        frozenset(
            {
                C.HISTORY,
                C.STATISTICS,
                C.ANALYSIS,
                C.GENERATION,
                C.BACKTESTING,
                C.SIMULATION,
                C.SETTLEMENT,
            }
        ),
    )
)
