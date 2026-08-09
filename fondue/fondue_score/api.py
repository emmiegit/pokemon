import json
import logging
import os
from typing import Any, NamedTuple, TypedDict, cast

import requests

API_ENDPOINT = "https://pokeapi.co/api/v2"
API_CACHE = True  # store results locally to save on request latency
API_CACHE_DIRECTORY = "cached_requests"

logger = logging.getLogger(__name__)


class NamelessSpecReference(TypedDict):
    url: str


class SpecReference(TypedDict):
    name: str
    url: str


class VersionGroupInfo(TypedDict):
    generation: SpecReference
    id: int
    move_learn_methods: list[SpecReference]
    name: str
    order: int
    pokedexes: list[SpecReference]
    regions: list[SpecReference]
    versions: list[SpecReference]


class MoveMachineSpec(TypedDict):
    machine: NamelessSpecReference
    version_group: SpecReference


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
    machines: list[MoveMachineSpec]
    meta: MetaMoveInfo | None
    damage_class: SpecReference
    type: SpecReference
    target: SpecReference


class GameInfo(NamedTuple):
    generation: int
    version_group: str

    def __str__(self) -> str:
        return f"generation {self.generation} (game '{self.version_group}')"


def _cache_path(request_path: str) -> str:
    request_path = request_path.strip("/")
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


def _map_version_group_name(value: str) -> str:
    # Common or abbreviated names for convenience
    # Add items here as needed
    match value:
        case "hgss" | "heartgold" | "soulsilver":
            return "heartgold-soulsilver"
        case "plat":
            return "platinum"
        case _:
            return value


def _map_generation(value: str) -> int:
    # Avoid a request just for a number
    match value:
        case "generation-i":
            return 1
        case "generation-ii":
            return 2
        case "generation-iii":
            return 3
        case "generation-iv":
            return 4
        case "generation-v":
            return 5
        case "generation-vi":
            return 6
        case "generation-vii":
            return 7
        case "generation-viii":
            return 8
        case "generation-ix":
            return 9
        case _:
            raise ValueError(value)


def fetch_game_info(version_group: str) -> GameInfo:
    logger.info("Fetching version group information for '%s'", version_group)
    version_group = _map_version_group_name(version_group)
    data = cast(VersionGroupInfo, pokeapi_request(f"version-group/{version_group}"))
    generation = _map_generation(data["generation"]["name"])
    return GameInfo(
        generation=generation,
        version_group=data["name"],
    )


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
