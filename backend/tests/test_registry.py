from app.domain.games import Capability, GameStatus
from app.games import registry


def test_registry_has_nine_unique_games() -> None:
    modules = registry.all()
    slugs = [module.definition.slug for module in modules]
    assert len(slugs) == 9
    assert len(set(slugs)) == 9


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


def test_loteria_nacional_awaits_rules() -> None:
    module = registry.get("loteria_nacional")
    assert module is not None
    assert module.definition.status is GameStatus.AWAITING_RULES
    assert module.definition.capabilities == frozenset()
