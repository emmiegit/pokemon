import logging

from .api import PokemonInfo, TypeInfo
from .game import GameInfo

logger = logging.getLogger(__name__)


def get_pokemon_types(pokemon: PokemonInfo, game: GameInfo) -> list[TypeInfo]:
    logger.debug("Getting latest Pokémon types for %s", pokemon["name"])
    for past_types in pokemon["past_types"]:
        if game.latest_generation["name"] == past_types["generation"]["name"]:
            return past_types
    return pokemon["types"]
