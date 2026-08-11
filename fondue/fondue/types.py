import logging
from collections import defaultdict
from collections.abc import Iterable

from .api_types import PokemonInfo, TypeSpecReference
from .game import GameInfo

logger = logging.getLogger(__name__)

# {type_name: [pokemon]}
PokemonByType = dict[str, list[PokemonInfo]]


def get_pokemon_types(pokemon: PokemonInfo, game: GameInfo) -> list[TypeSpecReference]:
    logger.debug("Getting latest Pokémon types for %s", pokemon["name"])
    for past_types in pokemon["past_types"]:
        if game.latest_generation["name"] == past_types["generation"]["name"]:
            return past_types["types"]
    return pokemon["types"]


def group_pokemon_by_type(
    all_pokemon: Iterable[PokemonInfo],
    game: GameInfo,
) -> PokemonByType:
    types = defaultdict(list)
    for pokemon in all_pokemon:
        for p_type in get_pokemon_types(pokemon, game):
            p_type_name = p_type["type"]["name"]
            types[p_type_name].append(pokemon)
    return types
