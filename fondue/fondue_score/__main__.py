import argparse
import logging
import math
import sys
from typing import Final

from .game import get_game_info
from .move import calculate_damage_by_type, compile_moves_by_type
from .pokemon import (
    fetch_all_pokemon,
    fetch_all_pokemon_species,
    get_pokemon_bsts_by_type,
)
from .stats import get_pokemon_stats_by_name
from .types import group_pokemon_by_type

TYPE_COLUMN: Final[str] = "TYPE"
SCORE_COLUMN: Final[str] = "SCORE"
DAMAGE_COLUMN: Final[str] = "DAMAGE"
MOVE_COLUMN: Final[str] = "MOVES"


def digits(n: float) -> int:
    return math.ceil(math.log10(n + 1))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Fondue Scorer")
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
    all_species = fetch_all_pokemon_species(game)
    all_pokemon = fetch_all_pokemon(all_species)

    logger.info("Organizing Pokémon by type and stats")
    pokemon_stats = get_pokemon_stats_by_name(all_pokemon, game)
    pokemon_by_type = group_pokemon_by_type(all_pokemon, game)
    bsts_by_type = get_pokemon_bsts_by_type(pokemon_stats, pokemon_by_type)
    mean_bst_by_type = {
        type_name: sum(bsts) / len(bsts) for type_name, bsts in bsts_by_type.items()
    }

    logger.info("Calculating damage for all moves in %s", game)
    moves_by_type = calculate_damage_by_type(game)
    damage_compl = compile_moves_by_type(moves_by_type)
    bst_damage_totals = [
        mean_bst_by_type[compl.type] * compl.damage_total for compl in damage_compl
    ]

    # Display the results in a nice way
    type_name_length = max(len(stat.type) for stat in damage_compl) + 2
    bst_damage_digits = digits(max(bst_damage_totals)) + 3
    bst_damage_length = max(len(SCORE_COLUMN), bst_damage_digits)
    damage_digits = digits(max(compl.damage_total for compl in damage_compl)) + 3
    damage_length = max(len(DAMAGE_COLUMN), damage_digits)
    move_count_digits = digits(max(compl.move_count for compl in damage_compl))
    move_count_length = max(len(MOVE_COLUMN), move_count_digits)

    print(
        " ".join(
            (
                TYPE_COLUMN.center(type_name_length),
                SCORE_COLUMN.center(bst_damage_length),
                DAMAGE_COLUMN.center(damage_length),
                MOVE_COLUMN.center(move_count_length),
            )
        )
    )
    print(
        "="
        * (type_name_length + bst_damage_length + damage_length + move_count_length + 4)
    )

    # Each row of data
    for compl, bst_damage_total in zip(damage_compl, bst_damage_totals):
        type_name = compl.type.upper()
        print(
            f"{type_name:{type_name_length}} {bst_damage_total:{bst_damage_length}.1f} {compl.damage_total:{damage_length}.2f} {compl.move_count:{move_count_length}}"
        )
