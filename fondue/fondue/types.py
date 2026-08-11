import logging
from collections import defaultdict
from collections.abc import Iterable
from enum import Enum, unique

from .api import fetch_generation, fetch_type
from .api_types import DamageRelationInfo, PokemonInfo, TypeInfo, TypeSpecReference
from .game import GameInfo

logger = logging.getLogger(__name__)


@unique
class TypeEffectiveness(Enum):
    NORMAL = 1.0
    SUPEREFFECTIVE = 2.0
    RESISTED = 0.5
    IMMUNE = 0.0


# {type_name: [pokemon]}
PokemonByType = dict[str, list[PokemonInfo]]


def get_pokemon_types(pokemon: PokemonInfo, game: GameInfo) -> list[TypeSpecReference]:
    logger.debug("Getting latest Pokémon types for %s", pokemon["name"])

    types = pokemon["types"]
    largest_override: tuple[int, list[TypeSpecReference]] | None = None

    for past_types in pokemon["past_types"]:
        generation = fetch_generation(past_types["generation"]["name"])

        # Ignore any past types prior to the current generation
        if generation["id"] < game.generation:
            continue

        # Otherwise, we set the override
        # If there's no override, then set it
        # Otherwise, only if it's larger
        if largest_override is None or generation["id"] > largest_override[0]:
            largest_override = (generation["id"], past_types["types"])

    # We've checked all the types, now return the override if we found one
    # or the latest types otherwise
    if largest_override is None:
        return types

    _, types = largest_override
    return types

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
