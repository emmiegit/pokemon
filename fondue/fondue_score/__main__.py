import argparse
import logging
import sys

from .game import get_game_info
from .move import calculate_damage_by_type, compile_moves_by_type
from .pokemon import (
    fetch_all_pokemon,
    fetch_all_pokemon_species,
    get_pokemon_bsts_by_type,
)
from .stats import get_pokemon_stats_by_name
from .types import group_pokemon_by_type

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

    logger.info("Calculating damage for all moves in %s", game)
    moves_by_type = calculate_damage_by_type(game)
    damage_compl = compile_moves_by_type(moves_by_type)

    # Display the results in a nice way
    max_type_name_length = max(len(stat.type) for stat in damage_compl)
    for compl in damage_compl:
        type_name = compl.type.upper()
        print(
            f"{type_name:{max_type_name_length}} {compl.damage_total:.2f} ({compl.move_count} moves)"
        )
