from app.domain.games import Capability as C
from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition(
        "melate_retro",
        "Melate Retro",
        "combination",
        GameStatus.PLANNED,
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
