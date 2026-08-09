import argparse

from .move import compile_moves_by_type


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Fondue Scorer")
    argparser.add_argument(
        "generation",
        type=int,
        nargs="?",
        default=4,
        help="Which generation to run for",
    )
    args = argparser.parse_args()
    stats = compile_moves_by_type(args.generation)

    # Display the results in a nice way
    max_type_name_length = max(len(stat.type) for stat in stats)
    for stat in stats:
        type_name = stat.type.upper()
        print(
            f"{type_name:{max_type_name_length}} {stat.damage_total:.2f} ({stat.move_count} moves)"
        )
