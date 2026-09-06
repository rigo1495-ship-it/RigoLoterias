from app.domain.games import GameDefinition, GameModule, GameStatus

module = GameModule(
    GameDefinition(
        "loteria_nacional",
        "Lotería Nacional",
        "dedicated",
        GameStatus.AWAITING_RULES,
        frozenset(),
    )
)
