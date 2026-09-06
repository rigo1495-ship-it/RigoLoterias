from app.games.chispazo import module as chispazo
from app.games.gana_gato import module as gana_gato
from app.games.melate import module as melate
from app.games.melate_retro import module as melate_retro
from app.games.progol import module as progol
from app.games.progol_media_semana import module as progol_media_semana
from app.games.protouch import module as protouch
from app.games.tris import module as tris
from app.services.game_registry import GameRegistry


def build_registry() -> GameRegistry:
    return GameRegistry(
        (
            tris,
            melate,
            melate_retro,
            chispazo,
            gana_gato,
            progol,
            progol_media_semana,
            protouch,
        )
    )


registry = build_registry()
