import math


def digits(n: float) -> int:
    return math.ceil(math.log10(n + 1))
