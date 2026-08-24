import logging
from collections import defaultdict
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from enum import Enum, unique
from typing import NamedTuple

from .api import fetch_generation, fetch_type
from .api_types import (
    DamageRelationInfo,
    PokemonInfo,
    SpecReference,
    TypeInfo,
    TypeSpecReference,
)
from .game import GameInfo
from .move import MoveCompilationForType

logger = logging.getLogger(__name__)


@unique
class TypeEffectiveness(Enum):
    NORMAL = 1.0
    SUPEREFFECTIVE = 2.0
    QUAD_EFFECTIVE = 4.0
    RESISTED = 0.5
    DOUBLE_RESISTED = 0.25
    IMMUNE = 0.0

    def __add__(self, other) -> "TypeEffectiveness":
        new_value = self.value * other.value
        return TypeEffectiveness(new_value)

    def __mul__(self, other) -> "TypeEffectiveness":
        return self + other


# {type_name: [pokemon]}
PokemonByType = dict[str, list[PokemonInfo]]

# {(attacking_type_name, defending_type_name): TypeEffectiveness}
TypeEffectivenessMatrix = dict[tuple[str, str], TypeEffectiveness]

# the types for one particular mon (always 1 or 2 long, but you know)
PokemonTyping = tuple[str, ...]

# all type combinations found across all pokemon in this game, with counts
AllPokemonTypings = Mapping[PokemonTyping, int]


class DefensiveCompilationForType(NamedTuple):
    typing: PokemonTyping
    recv_damage_total: float
    recv_bst_damage_total: float
    pokemon_count: int


def get_pokemon_types(
    pokemon: PokemonInfo,
    game: GameInfo,
) -> list[TypeSpecReference]:
    logger.debug("Getting latest Pokémon types for %s", pokemon["name"])

    types = pokemon["types"]
    override: tuple[int, list[TypeSpecReference]] | None = None

    for past_types in pokemon["past_types"]:
        generation = fetch_generation(past_types["generation"]["name"])

        # Ignore any past types prior to the current generation
        if generation["id"] < game.generation:
            continue

        # Otherwise, we set the override
        # We're looking for the largest generation in the past list
        # to set as our override
        # If there's no override, then always set it
        if override is None or generation["id"] > override[0]:
            override = (generation["id"], past_types["types"])

    if override is not None:
        _, types = override

    return types


def fetch_all_types(game: GameInfo) -> list[TypeInfo]:
    types = []
    for type_spec in game.all_types():
        p_type = fetch_type(type_spec["url"])
        if not p_type["pokemon"]:
            # weird type, like shadow. skip
            continue

        types.append(p_type)
    return types


def type_in_spec_list(
    type_name: str,
    type_specs: Iterable[SpecReference],
) -> bool:
    for type_spec in type_specs:
        if type_spec["name"] == type_name:
            return True
    return False


def get_type_damage_relations(
    p_type: TypeInfo,
    game: GameInfo,
) -> DamageRelationInfo:
    logger.debug("Getting latest Pokémon type damage relations for %s", p_type["name"])

    # See get_pokemon_types() for logic
    relations = p_type["damage_relations"]
    override: tuple[int, DamageRelationInfo] | None = None

    for past_relations in p_type["past_damage_relations"]:
        generation = fetch_generation(past_relations["generation"]["name"])
        if generation["id"] < game.generation:
            continue

        if override is None or generation["id"] > override[0]:
            override = (generation["id"], past_relations["damage_relations"])

    if override is not None:
        _, relations = override

    return relations


def get_type_damage_matrix(
    all_types: list[TypeInfo],
    game: GameInfo,
) -> TypeEffectivenessMatrix:
    matrix: TypeEffectivenessMatrix = {}
    for attacking_type in all_types:
        attacking_type_name = attacking_type["name"]
        attacking_relations = get_type_damage_relations(attacking_type, game)
        for defending_type in all_types:
            defending_type_name = defending_type["name"]

            if type_in_spec_list(
                defending_type_name,
                attacking_relations["double_damage_to"],
            ):
                effectiveness = TypeEffectiveness.SUPEREFFECTIVE
            elif type_in_spec_list(
                defending_type_name,
                attacking_relations["half_damage_to"],
            ):
                effectiveness = TypeEffectiveness.RESISTED
            elif type_in_spec_list(
                defending_type_name,
                attacking_relations["no_damage_to"],
            ):
                effectiveness = TypeEffectiveness.IMMUNE
            else:
                effectiveness = TypeEffectiveness.NORMAL

            matrix[(attacking_type_name, defending_type_name)] = effectiveness
    return matrix


def get_typing_effectiveness(
    attacking_type: str,
    defending_typing: PokemonTyping,
    matrix: TypeEffectivenessMatrix,
) -> TypeEffectiveness:
    effectiveness = TypeEffectiveness.NORMAL
    for defending_type in defending_typing:
        effectiveness *= matrix[(attacking_type, defending_type)]
    return effectiveness


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


def get_unique_pokemon_typings(
    all_pokemon: Iterable[PokemonInfo],
    game: GameInfo,
) -> AllPokemonTypings:
    typings: MutableMapping[PokemonTyping, int] = defaultdict(int)
    for pokemon in all_pokemon:
        typing = tuple(ty["type"]["name"] for ty in get_pokemon_types(pokemon, game))
        typings[typing] += 1
    return typings


def calculate_defensive_scores_by_pokemon_typings(
    damage_compl: Sequence[MoveCompilationForType],
    matrix: TypeEffectivenessMatrix,
    all_pokemon_typings: AllPokemonTypings,
) -> list[DefensiveCompilationForType]:
    logger.info("Calculating defensive scores by type...")
    defense_by_type = []
    for defending_typing, pokemon_count in all_pokemon_typings.items():
        damage_total = 0.0
        bst_damage_total = 0.0

        for compl in damage_compl:
            attacking_type = compl.type
            effectiveness = get_typing_effectiveness(
                attacking_type,
                defending_typing,
                matrix,
            )
            damage_total += compl.damage_total * effectiveness.value
            bst_damage_total += compl.bst_damage_total * effectiveness.value

        defense_by_type.append(
            DefensiveCompilationForType(
                typing=defending_typing,
                recv_damage_total=damage_total,
                recv_bst_damage_total=bst_damage_total,
                pokemon_count=pokemon_count,
            )
        )
    defense_by_type.sort(key=lambda compl: compl.recv_bst_damage_total)
    return defense_by_type
