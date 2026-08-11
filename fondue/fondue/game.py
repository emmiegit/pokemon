import logging
from typing import NamedTuple

from .api import (
    fetch_generation,
    fetch_version_group,
)
from .api_types import (
    GenerationInfo,
    SpecReference,
    VersionGroupInfo,
)

logger = logging.getLogger(__name__)


def _map_version_group_name(value: str) -> str:
    # Common or abbreviated names for convenience
    # Add items here as needed
    match value:
        case "rb" | "red" | "blue":
            return "red-blue"
        case "y":
            return "yellow"
        case "gs" | "gold" | "silver":
            return "gold-silver"
        case "c":
            return "crystal"
        case "rs" | "ruby" | "sapphire":
            return "ruby-sapphire"
        case "e":
            return "emerald"
        case "firered" | "fire-red" | "fr" | "leafgreen" | "leaf-green" | "lg":
            return "firered-leafgreen"
        case "dp" | "diamond" | "pearl":
            return "diamond-pearl"
        case "plat":
            return "platinum"
        case "hgss" | "heartgold" | "soulsilver":
            return "heartgold-soulsilver"
        case "bw" | "black" | "white":
            return "black-white"
        case "xy" | "x" | "y":
            return "x-y"
        case (
            "oras"
            | "omegaruby"
            | "omega-ruby"
            | "or"
            | "alphasapphire"
            | "alpha-sapphire"
            | "as"
        ):
            return "omega-ruby-alpha-sapphire"
        case "sm" | "sun" | "moon":
            return "sun-moon"
        case (
            "usum" | "ultrasun" | "ultra-sun" | "us" | "ultamoon" | "ultra-moon" | "um"
        ):
            return "ulta-sun-ultra-moon"
        case "lets-go-pikachu" | "lgp" | "lets-go-eevee" | "lge":
            return "lets-go-pikachu-lets-go-eevee"
        case "ss" | "sword" | "shield":
            return "sword-shield"
        case _:
            return value


class GameInfo(NamedTuple):
    generations: list[GenerationInfo]
    version_group_data: VersionGroupInfo

    @property
    def latest_generation(self) -> GenerationInfo:
        return self.generations[-1]

    @property
    def generation(self) -> int:
        return self.latest_generation["id"]

    @property
    def version_group(self) -> str:
        return self.version_group_data["name"]

    def generation_from_name(self, generation_name: str) -> int | None:
        for gen in self.generations:
            if gen["name"] == generation_name:
                return gen["id"]
        return None

    def all_moves(self) -> list[SpecReference]:
        moves: list[SpecReference] = []
        for gen in self.generations:
            moves.extend(gen["moves"])
        return moves

    def all_types(self) -> list[SpecReference]:
        types: list[SpecReference] = []
        for gen in self.generations:
            types.extend(gen["types"])
        return types

    def all_species(self) -> list[SpecReference]:
        species: list[SpecReference] = []
        for gen in self.generations:
            species.extend(gen["pokemon_species"])
        return species

    def __str__(self) -> str:
        return f"generation {self.generation} (game '{self.version_group}')"


def get_game_info(version_group: str) -> GameInfo:
    logger.info("Fetching version group information for '%s'", version_group)

    version_group = _map_version_group_name(version_group)
    version_group_data = fetch_version_group(version_group)

    latest_generation = fetch_generation(version_group_data["generation"]["name"])
    generations = []
    for n in range(1, latest_generation["id"]):
        generations.append(fetch_generation(n))
    generations.append(latest_generation)

    return GameInfo(
        generations=generations,
        version_group_data=version_group_data,
    )
