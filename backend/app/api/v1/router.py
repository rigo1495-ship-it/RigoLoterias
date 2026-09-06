from fastapi import APIRouter, HTTPException

from app.domain.games import Capability
from app.games import registry
from app.schemas.games import CapabilityErrorResponse, GameResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "RigoLoterias"}


@router.get("/games", response_model=list[GameResponse])
def games() -> list[GameResponse]:
    return [GameResponse.from_definition(module.definition) for module in registry.all()]


@router.get("/games/{game}", response_model=GameResponse)
def game(game: str) -> GameResponse:
    module = registry.get(game)
    if module is None:
        raise HTTPException(
            status_code=404,
            detail={
                "game": game,
                "capability": "registry",
                "status": "unknown",
                "message": f"Game '{game}' is not registered.",
            },
        )
    return GameResponse.from_definition(module.definition)


@router.get(
    "/games/{game}/capabilities/{capability}",
    responses={501: {"model": CapabilityErrorResponse}},
)
def unavailable_capability(game: str, capability: str) -> None:
    module = registry.get(game)
    if module is None:
        raise HTTPException(
            status_code=404,
            detail={
                "game": game,
                "capability": capability,
                "status": "unknown",
                "message": f"Game '{game}' is not registered.",
            },
        )
    if capability not in {item.value for item in Capability}:
        raise HTTPException(
            status_code=404,
            detail={
                "game": game,
                "capability": capability,
                "status": module.definition.status,
                "message": f"Capability '{capability}' is not recognized.",
            },
        )
    raise HTTPException(
        status_code=501,
        detail={
            "game": game,
            "capability": capability,
            "status": module.definition.status,
            "message": f"Capability '{capability}' is not implemented for '{game}' in Phase A.",
        },
    )
