# Architecture overview

RigoLoterias separates HTTP delivery, application services, domain contracts, engines and
game modules. The dependency direction points inward: game logic may use domain contracts,
while domain code must not depend on FastAPI, SQLAlchemy or React.

The game registry is the authoritative runtime catalog. A `GameModule` declares metadata,
capabilities and optional implementations. A declared capability describes the intended
surface; it does not make a game available. Only a completed, validated phase may change a
game status to `available`.

Shared persistence stores identity, provenance and execution metadata. Incompatible result
shapes will use engine-specific tables added in later migrations rather than a rigid universal
result table.

