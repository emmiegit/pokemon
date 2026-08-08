def normalize_spread(stats):
    total = sum(stats)
    count = len(stats)
    return [(stat / total) * count for stat in stats]



TEMPLATE_SPREADS = [
    ("flat", [1, 1, 1, 1, 1, 1]),
    ("staircase", normalize_spread([10, 20, 30, 40, 50, 60])),
    ("reverse staircase", normalize_spread([60, 50, 40, 30, 20, 10])),
    ("fork", normalize_spread([0, 100, 0, 100, 0, 100])),
    # Below 90 is "no speed"
    ("mans", normalize_spread([80, 100, 80, 100, 80, 0])),
    ("sentor", normalize_spread([100, 20, 100, 20, 100, 0])),
    # HP 50-80
    # ATK 200
    # DEF 50-80
    # SPA 0
    # SPD 50-80
    # SPE 90-110
    ("ideal atk", normalize_spread([80, 200, 80, 0, 80, 110])),
    ("ideal spa", normalize_spread([80, 0, 80, 200, 80, 110])),
    # Cheezinator spreads are where one defense stat is below 50
    ("cheezinator atk/def", normalize_spread([80, 200, 0, 0, 80, 110])),
    ("cheezinator spa/def", normalize_spread([80, 0, 0, 200, 80, 110])),
    ("cheezinator atk/spd", normalize_spread([80, 200, 80, 0, 0, 110])),
    ("cheezinator spa/spd", normalize_spread([80, 0, 80, 200, 0, 110])),
]


def calculate_error(spread1, spread2):
    errors = [abs(stat1 - stat2) for stat1, stat2 in zip(spread1, spread2)]
    return sum(errors), errors


def calculate_fit(total_error, count):
    return (2 * count - total_error) / (2 * count)


def compare_spreads(spread):
    results = []
    for name, template_spread in TEMPLATE_SPREADS:
        total_error, error = calculate_error(spread, template_spread)
        fit = calculate_fit(total_error, len(spread))
        results.append((name, total_error, error, fit))

    results.sort(key=lambda x: x[3])
    return results
