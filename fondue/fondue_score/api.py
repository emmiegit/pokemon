import json
import logging
import os
from typing import Any, cast

import requests

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
API_CACHE = True  # store results locally to save on request latency
API_CACHE_DIRECTORY = "cached_requests"

logger = logging.getLogger(__name__)


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


def fetch_pokemon_form(url: str) -> PokemonFormInfo:
    assert "/pokemon-form/" in url
    data = pokeapi_request(url)
    return cast(PokemonFormInfo, data)
