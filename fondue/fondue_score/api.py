import logging
from typing import Any, TypedDict, cast

import requests

API_ENDPOINT = "https://pokeapi.co/api/v2"

logger = logging.getLogger(__name__)


class SpecReference(TypedDict):
    name: str
    url: str


class MetaMoveInfo(TypedDict):
    category: SpecReference
    ailment: SpecReference
    ailment_chance: int
    crit_rate: int
    drain: int
    flinch_chance: int
    healing: int
    min_hits: int | None
    max_hits: int | None
    min_turns: int | None
    max_turns: int | None
    stat_chance: int


class MoveInfo(TypedDict):
    id: int
    name: str
    power: int | None
    accuracy: int | None
    pp: int
    priority: int
    effect_change: int
    meta: MetaMoveInfo | None
    damage_class: SpecReference
    type: SpecReference
    target: SpecReference


def pokeapi_request(path: str) -> dict[str, Any]:
    if path.startswith(API_ENDPOINT):
        url = path
        path = url.removeprefix(API_ENDPOINT)
    else:
        url = f"{API_ENDPOINT}/{path}"

    logger.debug("Fetching from PokéAPI: %s", path)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def fetch_all_moves(generation: int) -> list[SpecReference]:
    logger.info("Fetching all moves for generation %d", generation)
    moves = []
    for current_gen in range(1, generation + 1):
        logger.debug("Fetching generation %d moves...", current_gen)
        data = pokeapi_request(f"generation/{current_gen}")
        moves.extend(data["moves"])
    return moves


def fetch_move_info(url: str) -> MoveInfo:
    data = pokeapi_request(url)
    return cast(MoveInfo, data)
