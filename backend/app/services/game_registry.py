from collections.abc import Iterable

from app.domain.games import GameModule


class GameRegistry:
    def __init__(self, modules: Iterable[GameModule] = ()) -> None:
        self._modules: dict[str, GameModule] = {}
        for module in modules:
            self.register(module)

    def register(self, module: GameModule) -> None:
        slug = module.definition.slug
        if not slug or slug in self._modules:
            raise ValueError(f"Duplicate or empty game slug: {slug!r}")
        self._modules[slug] = module

    def all(self) -> tuple[GameModule, ...]:
        return tuple(self._modules.values())

    def get(self, slug: str) -> GameModule | None:
        return self._modules.get(slug)
