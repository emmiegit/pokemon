import json
import logging
import os
from typing import Any, TypedDict, cast

import requests

API_ENDPOINT = "https://pokeapi.co/api/v2"
API_CACHE = True  # store results locally to save on request latency
API_CACHE_DIRECTORY = "cached_requests"

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


def _cache_path(request_path: str) -> str:
    file_name = request_path.replace("/", ".") + ".json"
    return os.path.join(API_CACHE_DIRECTORY, file_name)


def _cache_store(file_path: str, data: dict[str, Any]) -> None:
    if not API_CACHE:
        return

    logger.debug("Storing request data to cache file %s", file_path)
    os.makedirs(API_CACHE_DIRECTORY, exist_ok=True)
    with open(file_path, "w") as file:
        json.dump(data, file)


def _cache_load(file_path: str) -> dict[str, Any]:
    if not API_CACHE:
        raise RuntimeError("API caching is not enabled")

    logger.debug("Loading request data from cache file %s", file_path)
    with open(file_path) as file:
        return json.load(file)


def pokeapi_request(path: str) -> dict[str, Any]:
    if path.startswith(API_ENDPOINT):
        url = path
        path = url.removeprefix(API_ENDPOINT)
    else:
        url = f"{API_ENDPOINT}/{path}"

    cache_path = _cache_path(path)
    if API_CACHE and os.path.isfile(cache_path):
        return _cache_load(cache_path)

    logger.debug("Fetching from PokéAPI: %s", path)
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    _cache_store(cache_path, data)
    return data


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
