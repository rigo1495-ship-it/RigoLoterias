from app.domain.games import Capability, GameStatus
from app.games import registry


def test_registry_has_eight_unique_games() -> None:
    modules = registry.all()
    slugs = [module.definition.slug for module in modules]
    assert len(slugs) == 8
    assert len(set(slugs)) == 8


def test_registry_statuses_and_capabilities_are_valid() -> None:
    for module in registry.all():
        assert isinstance(module.definition.status, GameStatus)
        assert all(isinstance(item, Capability) for item in module.definition.capabilities)
        if module.definition.slug in {
            "tris",
            "melate",
            "melate_retro",
            "chispazo",
            "gana_gato",
            "progol",
            "progol_media_semana",
            "protouch",
        }:
            assert module.definition.status is GameStatus.AVAILABLE
        else:
            assert module.definition.status is not GameStatus.AVAILABLE


def test_registry_contains_only_the_eight_supported_games() -> None:
    assert registry.get("loteria_nacional") is None
    assert len(registry.all()) == 8
