from typing import Any, NamedTuple

import requests

API_ENDPOINT = "https://pokeapi.co/api/v2"


class SpecReference(NamedTuple):
    name: str
    url: str


class MetaMoveInfo(NamedTuple):
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


class MoveInfo(NamedTuple):
    id: int
    power: int
    accuracy: int
    pp: int
    priority: int
    effect_change: int
    meta: MetaMoveInfo
    damage_class: SpecReference
    type: SpecReference


def pokeapi_request(path: str) -> dict[str, Any]:
    if path.startswith(API_ENDPOINT):
        url = path
    else:
        url = f"{API_ENDPOINT}/{path}"

    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def fetch_all_moves(generation: int) -> list[SpecReference]:
    data = pokeapi_request(f"generation/{generation}")
    return data["moves"]


def fetch_move_info(url: str) -> MoveInfo:
    return pokeapi_request(url)
