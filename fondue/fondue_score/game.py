import logging
from typing import NamedTuple

from .api import fetch_version_group

logger = logging.getLogger(__name__)


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


class GameInfo(NamedTuple):
    generation: int
    version_group_data: VersionGroupInfo

    @property
    def version_group(self) -> str:
        return self.version_group_data["name"]

    def __str__(self) -> str:
        return f"generation {self.generation} (game '{self.version_group}')"


def get_game_info(version_group: str) -> GameInfo:
    logger.info("Fetching version group information for '%s'", version_group)
    version_group = _map_version_group_name(version_group)
    data = fetch_version_group(version_group)
    generation = _map_generation(data["generation"]["name"])
    return GameInfo(
        generation=generation,
        version_group_data=data,
    )
