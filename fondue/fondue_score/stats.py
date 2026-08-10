import logging
from typing import Iterable, Final, Mapping

from .api import PokemonInfo, StatInfo
from .game import GameInfo

logger = logging.getLogger(__name__)

# Stats that used to exist, but were removed in later gens
# (last_generation_id with the stat, stat_name)
REMOVED_STATS: Final[list[tuple[int, str]]] = [(1, "special")]

# Stats that were added in later gens
# (first_generation_id with the stat, stat_name)
ADDED_STATS: Final[list[tuple[int, str]]] = [(2, "special-attack"), (2, "special-defense")]

# Key is the stat_name
CurrentPokemonStats = dict[str, StatInfo]


def stat_is_removed(stat_name: str, generation: int) -> bool:
    for last_generation_id, removed_stat_name in REMOVED_STATS:
        if stat_name == removed_stat_name and generation > last_generation_id:
            return True
    return False


def get_pokemon_stats(pokemon: PokemonInfo, game: GameInfo) -> CurrentPokemonStats:
    logger.debug("Getting latest Pokémon stats for %s", pokemon["name"])
    stats = {stat["stat"]["name"]: stat for stat in pokemon["stats"]}
    for all_past_stats in pokemon["past_stats"]:
        past_generation_name = all_past_stats["generation"]["name"]
        gen = game.generation_from_name(past_generation_name)
        if gen is None:
            # this is for a later generation, skip
            continue

        for past_stat in all_past_stats["stats"]:
            # filter out removed stats
            stat_name = past_stat["stat"]["name"]
            if not stat_is_removed(stat_name, game.generation):
                logger.debug(
                    "Overriding past stat %s from generation %s",
                    stat_name,
                    past_generation_name,
                )
                stats[stat_name] = past_stat

    # filter out stats added later
    for first_generation_id, added_stat_name in ADDED_STATS:
        if game.generation < first_generation_id:
            del stats[added_stat_name]

    return stats


def get_pokemon_stats_by_name(
    all_pokemon: Iterable[PokemonInfo],
    game: GameInfo,
) -> dict[str, CurrentPokemonStats]:
    return {
        pokemon["name"]: get_pokemon_stats(pokemon, game) for pokemon in all_pokemon
    }


def get_base_stat_total(stats: CurrentPokemonStats) -> int:
    return sum(stat["base_stat"] for stat in stats.values())
