#!/usr/bin/env python3

from spread_classifier import normalize_spread, compare_spreads

def check_spread(spread):
    assert len(spread) == 6, "requires all 6 stats (HP, ATK, DEF, SPA, SPD, SPE)"
    spread = normalize_spread(spread)
    print(spread)
    results = compare_spreads(spread)
    for name, total_error, error, fit in results:
        print(f"{name} {total_error:.2f} {fit:.2f}")
    print(f"Best match: {name} {fit * 100:.1f}% fit")


if __name__ == "__main__":
    check_spread([105, 185, 35, 40, 77, 102])
