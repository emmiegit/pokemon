import argparse
import logging
import sys
from collections.abc import Sequence
from typing import Final

from .game import get_game_info
from .move import (
    MoveCompilationForType,
    calculate_damage_by_type,
    compile_moves_by_type,
)
from .pokemon import (
    fetch_all_pokemon,
    fetch_all_pokemon_species,
    get_pokemon_bsts_by_type,
)
from .stats import get_pokemon_stats_by_name
from .types import (
    DefensiveCompilationForType,
    calculate_defensive_scores_by_pokemon_typings,
    fetch_all_types,
    get_type_damage_matrix,
    group_pokemon_by_type,
    group_pokemon_by_typings,
)
from .util import digits

OFFENSE_TITLE: Final[str] = "OFFENSE"
DEFENSE_TITLE: Final[str] = "DEFENSE"

TYPE_COLUMN: Final[str] = "TYPE"
SCORE_COLUMN: Final[str] = "SCORE"
DAMAGE_COLUMN: Final[str] = "DAMAGE"
MOVE_COLUMN: Final[str] = "MOVES"
BST_MEAN_COLUMN: Final[str] = "AVG-BST"
POKEMON_SHORT_COLUMN: Final[str] = "PKMN"

TYPING_COLUMN: Final[str] = "TYPING"
POKEMON_FULL_COLUMN: Final[str] = "POKÉMON"

SAMPLE_POKEMON_FOR_TYPE: Final[int] = 3


def print_offense_results(damage_compl: Sequence[MoveCompilationForType]):
    type_name_length = max(len(stat.type) for stat in damage_compl) + 2
    bst_damage_digits = (
        digits(max(compl.bst_damage_total for compl in damage_compl)) + 3
    )
    bst_damage_length = max(len(SCORE_COLUMN), bst_damage_digits)
    damage_digits = digits(max(compl.damage_total for compl in damage_compl)) + 4
    damage_length = max(len(DAMAGE_COLUMN), damage_digits)
    move_count_digits = digits(max(compl.move_count for compl in damage_compl))
    move_count_length = max(len(MOVE_COLUMN), move_count_digits)
    mean_bst_digits = digits(max(mean_bst_by_type.values())) + 2
    mean_bst_length = max(len(BST_MEAN_COLUMN), mean_bst_digits)
    pokemon_count_digits = digits(max(len(bsts) for bsts in bsts_by_type.values())) + 1
    pokemon_count_length = max(len(POKEMON_SHORT_COLUMN), pokemon_count_digits)

    full_width = (
        type_name_length
        + bst_damage_length
        + damage_length
        + move_count_length
        + mean_bst_length
        + pokemon_count_length
        + 6
    )

    print(OFFENSE_TITLE.center(full_width))
    print()
    print(
        " ".join(
            (
                TYPE_COLUMN.center(type_name_length),
                SCORE_COLUMN.center(bst_damage_length),
                DAMAGE_COLUMN.center(damage_length),
                MOVE_COLUMN.center(move_count_length),
                BST_MEAN_COLUMN.center(mean_bst_length),
                POKEMON_SHORT_COLUMN.center(pokemon_count_length),
            )
        )
    )
    print("=" * full_width)

    for compl in damage_compl:
        type_name = compl.type.upper()
        print(
            f"{type_name:{type_name_length}} {compl.bst_damage_total:{bst_damage_length}.1f} {compl.damage_total:{damage_length}.2f} {compl.move_count:{move_count_length}} {compl.mean_bst:{mean_bst_length}.1f} {compl.pokemon_count:{pokemon_count_length}}"
        )


def print_defense_results(defense_compl: Sequence[DefensiveCompilationForType]):
    # Pre-cacluate pokemon lists for length calculations
    pokemon_strings = []
    for compl in defense_compl:
        pokemon_list = compl.pokemon_list
        if len(pokemon_list) > SAMPLE_POKEMON_FOR_TYPE:
            pokemon_list = list(compl.pokemon_list[:SAMPLE_POKEMON_FOR_TYPE])
            pokemon_list.append("...")

        pokemon_strings.append(", ".join(name.upper() for name in pokemon_list))

    typing_name_length = max(sum(map(len, compl.typing)) for compl in defense_compl) + 1
    bst_damage_digits = (
        digits(max(compl.recv_bst_damage_total for compl in defense_compl)) + 3
    )
    bst_damage_length = max(len(SCORE_COLUMN), bst_damage_digits)
    damage_digits = digits(max(compl.recv_damage_total for compl in defense_compl)) + 4
    damage_length = max(len(DAMAGE_COLUMN), damage_digits)
    pokemon_length = max(map(len, pokemon_strings))

    full_width = (
        typing_name_length + bst_damage_length + damage_length + pokemon_length + 3
    )

    print()
    print()
    print(DEFENSE_TITLE.center(full_width))
    print()
    print(
        " ".join(
            (
                TYPING_COLUMN.center(typing_name_length),
                SCORE_COLUMN.center(bst_damage_length),
                DAMAGE_COLUMN.center(damage_length),
                POKEMON_FULL_COLUMN.center(pokemon_length),
            )
        )
    )
    print("=" * full_width)

    for compl, pokemon_str in zip(defense_compl, pokemon_strings):
        typing_str = "/".join(ty.upper() for ty in compl.typing)
        print(
            f"{typing_str:{typing_name_length}} {compl.recv_bst_damage_total:{bst_damage_length}.1f} {compl.recv_damage_total:{damage_length}.1f} {pokemon_str}"
        )


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Fondue Scorer")
    argparser.add_argument(
        "-E",
        "--fully-evolved",
        action="store_true",
        help="Only consider fully-evolved Pokémon",
    )
    argparser.add_argument(
        "-L",
        "--allow-defending-legendaries",
        action="store_true",
        help="Consider legendaries/mystical Pokémon in defensive typing analysis",
    )
    argparser.add_argument(
        "-b",
        "--max-defending-bst",
        type=int,
        default=599,
        help="Only consider Pokémon with BSTs lower than this value in defensive typing analysis (0 for no limit)",
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        help="Enable logging for scorer execution",
    )
    argparser.add_argument(
        "game",
        help="What game/version group to run the calculations for",
    )
    args = argparser.parse_args()

    exclude_defending_legendaries = not args.allow_defending_legendaries
    exclude_defending_bst_above = (
        None if args.max_defending_bst <= 0 else args.max_defending_bst
    )

    # Set up logger (if enabled)
    logger = logging.getLogger(__package__)
    if args.verbose > 0:
        logger.setLevel(logging.DEBUG if args.verbose > 1 else logging.INFO)
        log_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)

    # Fetch results
    logger.debug("Fetching game / verison group information")
    game = get_game_info(args.game)

    logger.info("Fetching Pokémon information for %s", game)
    all_species = fetch_all_pokemon_species(game, fully_evolved_only=args.fully_evolved)
    all_pokemon = fetch_all_pokemon(all_species, game)

    logger.info("Organizing Pokémon by type and stats")
    pokemon_stats = get_pokemon_stats_by_name(all_pokemon, game)
    pokemon_by_type = group_pokemon_by_type(all_pokemon, game)
    bsts_by_type = get_pokemon_bsts_by_type(pokemon_stats, pokemon_by_type)
    pokemon_counts_by_type = {
        type_name: len(bsts) for type_name, bsts in bsts_by_type.items()
    }
    mean_bst_by_type = {
        type_name: sum(bsts) / len(bsts) for type_name, bsts in bsts_by_type.items()
    }

    logger.info("Fetching Pokémon type information")
    all_types = fetch_all_types(game)
    pokemon_by_typings = group_pokemon_by_typings(
        all_pokemon,
        game,
        exclude_defending_legendaries=exclude_defending_legendaries,
        exclude_defending_bst_above=exclude_defending_bst_above,
        stats_by_name=pokemon_stats,
    )
    type_matrix = get_type_damage_matrix(all_types, game)

    logger.info("Calculating damage for all moves in %s", game)
    moves_by_type = calculate_damage_by_type(game)
    damage_compl = compile_moves_by_type(
        moves_by_type,
        mean_bst_by_type,
        pokemon_counts_by_type,
    )
    print_offense_results(damage_compl)

    logger.info("Calculating defensive typing for all Pokémon types")
    defense_compl = calculate_defensive_scores_by_pokemon_typings(
        damage_compl,
        type_matrix,
        pokemon_by_typings,
        pokemon_stats,
    )
    print_defense_results(defense_compl)
