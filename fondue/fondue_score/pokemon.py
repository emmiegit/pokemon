import logging
from collections.abc import Iterable

from .api import PokemonInfo, PokemonSpeciesInfo, fetch_pokemon, fetch_pokemon_species
from .game import GameInfo
from .stats import CurrentPokemonStats, get_base_stat_total
from .types import PokemonByType

logger = logging.getLogger(__name__)

PokemonBaseStatTotalsByType = dict[str, list[int]]


# Main fetch methods


def fetch_all_pokemon_species(game: GameInfo) -> list[PokemonSpeciesInfo]:
    logger.info("Fetching all Pokémon species")
    all_species = []
    for generation in game.generations:
        for species_spec in generation["pokemon_species"]:
            logger.info("Fetching Pokémon species %s", species_spec["name"])
            species = fetch_pokemon_species(species_spec["url"])
            all_species.append(species)
    return all_species


def fetch_all_pokemon(all_species: Iterable[PokemonSpeciesInfo]) -> list[PokemonInfo]:
    logger.info("Fetching all Pokémon")
    all_pokemon = []
    for species in all_species:
        for variety in species["varieties"]:
            logger.info("Fetching Pokémon %s", variety["pokemon"]["name"])
            pokemon = fetch_pokemon(variety["pokemon"]["url"])
            all_pokemon.append(pokemon)
    return all_pokemon


# Downstream aggregation methods


def get_pokemon_bsts_by_type(
    pokemon_stats: dict[str, CurrentPokemonStats],
    pokemon_by_type: PokemonByType,
) -> PokemonBaseStatTotalsByType:
    bsts_by_type = {}
    for p_type, pokemon_list in pokemon_by_type.items():
        bsts_by_type[p_type] = [
            get_base_stat_total(pokemon_stats[pokemon["name"]])
            for pokemon in pokemon_list
        ]
    return bsts_by_type
