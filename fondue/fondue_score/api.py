import json
import logging
import os
from typing import Any, TypedDict, cast

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


class GenerationInfo(TypedDict):
    id: int
    name: str
    main_region: SpecReference
    moves: list[SpecReference]
    pokemon_species: list[SpecReference]
    types: list[SpecReference]
    version_groups: list[SpecReference]


class MoveMachineSpec(TypedDict):
    machine: NamelessSpecReference
    version_group: SpecReference


class MachineInfo(TypedDict):
    id: int
    item: SpecReference
    move: SpecReference
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


class TypeInfo(TypedDict):
    slot: int
    type: SpecReference


class StatInfo(TypedDict):
    base_stat: int
    effort: int
    stat: SpecReference


class PastStatInfo(TypedDict):
    generation: SpecReference
    stats: list[StatInfo]


class PokemonInfo(TypedDict):
    id: int
    name: str
    species: SpecReference
    types: list[TypeInfo]
    forms: list[SpecReference]
    moves: list[SpecReference]
    is_default: bool
    base_experience: int
    height: int
    weight: int
    stats: list[StatInfo]
    past_stats: list[PastStatInfo]


class PokemonSpeciesVarietyInfo(TypedDict):
    is_default: bool
    pokemon: SpecReference


class PokemonSpeciesInfo(TypedDict):
    id: int
    name: str
    order: int
    evolution_chain: NamelessSpecReference
    evolves_from_species: SpecReference
    varieties: list[PokemonSpeciesVarietyInfo]
    shape: SpecReference
    forms_switchable: bool
    gender_rate: int
    has_gender_differences: bool
    generation: SpecReference
    growth_rate: SpecReference
    hatch_counter: int
    egg_groups: list[SpecReference]
    is_baby: bool
    is_legendary: bool
    is_mythical: bool


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


def fetch_version_group(version_group: str) -> VersionGroupInfo:
    data = pokeapi_request(f"version-group/{version_group}")
    return cast(VersionGroupInfo, data)


def fetch_generation(generation: str | int) -> GenerationInfo:
    data = pokeapi_request(f"generation/{generation}")
    return cast(GenerationInfo, data)


def fetch_machine(url: str) -> MachineInfo:
    assert "/machine/" in url
    data = pokeapi_request(url)
    return cast(MachineInfo, data)


def fetch_move_info(url: str) -> MoveInfo:
    assert "/move/" in url
    data = pokeapi_request(url)
    return cast(MoveInfo, data)


def fetch_pokemon(url: str) -> PokemonInfo:
    assert "/pokemon/" in url
    data = pokeapi_request(url)
    return cast(PokemonInfo, data)


def fetch_pokemon_species(url: str) -> PokemonSpeciesInfo:
    assert "/pokemon-species/" in url
    data = pokeapi_request(url)
    return cast(PokemonSpeciesInfo, data)
