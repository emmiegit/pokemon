import logging
from collections.abc import Iterable

from .api import (
    fetch_pokemon,
    fetch_pokemon_form,
    fetch_pokemon_species,
    fetch_version_group,
)
from .api_types import PokemonInfo, PokemonSpeciesInfo, SpecReference
from .game import GameInfo
from .stats import CurrentPokemonStats, get_base_stat_total
from .types import PokemonByType

logger = logging.getLogger(__name__)

PokemonBaseStatTotalsByType = dict[str, list[int]]


def fetch_all_pokemon_species(game: GameInfo) -> list[PokemonSpeciesInfo]:
    logger.info("Fetching all Pokémon species")
    all_species = []
    for generation in game.generations:
        for species_spec in generation["pokemon_species"]:
            logger.info("Fetching Pokémon species %s", species_spec["name"])
            species = fetch_pokemon_species(species_spec["url"])
            all_species.append(species)
    return all_species


def fetch_all_pokemon(
    all_species: Iterable[PokemonSpeciesInfo],
    game: GameInfo,
) -> list[PokemonInfo]:
    logger.info("Fetching all Pokémon")
    all_pokemon = []
    for species in all_species:
        for variety in species["varieties"]:
            logger.info("Fetching Pokémon %s", variety["pokemon"]["name"])
            pokemon = fetch_pokemon(variety["pokemon"]["url"])
            if any_pokemon_form_valid(pokemon["forms"], game):
                # At least one of these forms should be valid
                # for the game being played. If not, it must
                # be something like a mega-evolution in an
                # older generation.
                all_pokemon.append(pokemon)
    return all_pokemon


def any_pokemon_form_valid(forms: list[SpecReference], game: GameInfo) -> bool:
    for form_spec in forms:
        form = fetch_pokemon_form(form_spec["url"])
        version_group = fetch_version_group(form["version_group"]["name"])
        if game.generation_from_name(version_group["generation"]["name"]) is not None:
            # this is a generation valid for this game
            return True
    return False


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
