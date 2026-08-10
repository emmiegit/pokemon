import logging
from collections import defaultdict
from typing import Iterable

from .api import fetch_pokemon, fetch_pokemon_species, PokemonInfo, PokemonSpeciesInfo
from .game import GameInfo

logger = logging.getLogger(__name__)


def fetch_all_pokemon_species(game: GameInfo) -> list[PokemonSpeciesInfo]:
    all_species = []
    for generation in game.generations:
        for species_spec in generation["pokemon_species"]:
            logger.debug("Fetching Pokémon species %s", species_spec["name"])
            species = fetch_pokemon_species(species_spec["url"])
            all_species.append(species)
    return all_species


def fetch_all_pokemon(all_species: Iterable[PokemonSpeciesInfo]) -> list[PokemonInfo]:
    all_pokemon = []
    for species in all_species:
        for variety in species["varieties"]:
            logger.debug("Fetching Pokémon %s", variety["pokemon"]["name"])
            pokemon = fetch_pokemon(variety["pokemon"]["url"])
            all_pokemon.append(pokemon)
    return all_pokemon
