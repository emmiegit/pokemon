import logging
from typing import Final

from .api import PokemonInfo, StatInfo
from .game import GameInfo

logger = logging.getLogger(__name__)

# Stats that used to exist, but were removed in later gens
# (last_generation_id with the stat, stat_name)
REMOVED_STATS: Final[list[tuple[int, str]]] = [(1, "special")]


def stat_is_active(stat_name: str, generation: int) -> bool:
    for last_generation_id, removed_stat_name in REMOVED_STATS:
        if stat_name == removed_stat_name and generation > last_generation_id:
            return False
    return True


def get_pokemon_stats(pokemon: PokemonInfo, game: GameInfo) -> dict[str, StatInfo]:
    logger.debug("Getting latest Pokémon stats for %s", pokemon["name"])
    stats = {stat["name"]: stat for stat in pokemon["stats"]}
    for past_stats in pokemon["past_stats"]:
        gen = game.generation_from_name(past_stats["generation"]["name"])
        if gen is None:
            # this is for a later generation, skip
            continue

        for past_stat in past_stats["stats"]:
            # filter out removed stats
            stat_name = past_stat["name"]
            if stat_is_active(stat_name, game.generation):
                logger.debug(
                    "Overriding past stat %s from generation %s (base stat %d -> %d)",
                    stat_name,
                    past_stat["generation"]["name"],
                    stats[stat_name]["base_stat"],
                    past_stat["base_stat"],
                )
                stats[stat_name] = past_stat
    return stats
