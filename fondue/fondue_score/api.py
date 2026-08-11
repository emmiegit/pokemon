import logging
from typing import Any, cast

import requests

from .api_cache import cache_exists, cache_load, cache_store, get_cache_path
from .api_types import (
    GenerationInfo,
    MachineInfo,
    MoveInfo,
    PokemonFormInfo,
    PokemonInfo,
    PokemonSpeciesInfo,
    VersionGroupInfo,
)

API_ENDPOINT = "https://pokeapi.co/api/v2"

logger = logging.getLogger(__name__)


def pokeapi_request(path: str) -> dict[str, Any]:
    if path.startswith(API_ENDPOINT):
        url = path
        path = url.removeprefix(API_ENDPOINT)
    else:
        url = f"{API_ENDPOINT}/{path}"

    cache_path = get_cache_path(path)
    if cache_exists(cache_path):
        return cache_load(cache_path)

    logger.debug("Fetching from PokéAPI: %s", path)
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    cache_store(cache_path, data)
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


def fetch_pokemon_form(url: str) -> PokemonFormInfo:
    assert "/pokemon-form/" in url
    data = pokeapi_request(url)
    return cast(PokemonFormInfo, data)
