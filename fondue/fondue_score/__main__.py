import argparse
import logging
import sys

from .move import compile_moves_by_type

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Fondue Scorer")
    argparser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="Enable logging for scorer execution",
    )
    argparser.add_argument(
        "generation",
        type=int,
        nargs="?",
        default=4,
        help="Which generation to run for",
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
    logger.info("Calculating damage for all moves in generation %d", args.generation)
    stats = compile_moves_by_type(args.generation)

    # Display the results in a nice way
    max_type_name_length = max(len(stat.type) for stat in stats)
    for stat in stats:
        type_name = stat.type.upper()
        print(
            f"{type_name:{max_type_name_length}} {stat.damage_total:.2f} ({stat.move_count} moves)"
        )
