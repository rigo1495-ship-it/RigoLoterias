from app.domain.games import Capability as C
from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition(
        "gana_gato",
        "Gana Gato",
        "board",
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
