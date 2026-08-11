def get_crit_chance(generation: int, crit_rate: int) -> float:
    match generation:
        case 1:
            raise NotImplementedError
        case 2:
            return gen2_crit_chance(crit_rate)
        case 3 | 4 | 5:
            return gen3to5_crit_chance(crit_rate)
        case 6:
            return gen6_crit_chance(crit_rate)
        case 7 | 8 | 9:
            return gen7plus_crit_chance(crit_rate)
        case _:
            raise ValueError(f"Unknown generation value: {generation}")


def gen2_crit_chance(crit_rate: int) -> float:
    match crit_rate:
        case 0:
            return 17 / 256
        case 1:
            return 1 / 8
        case 2:
            return 1 / 4
        case 3:
            return 85 / 256
        case 4:
            return 1 / 2
        case _:
            raise ValueError(crit_rate)


def gen3to5_crit_chance(crit_rate: int) -> float:
    match crit_rate:
        case 0:
            return 1 / 16
        case 1:
            return 1 / 8
        case 2:
            return 1 / 4
        case 3:
            return 1 / 3
        case 4:
            return 1 / 2
        case _:
            raise ValueError(crit_rate)


def gen6_crit_chance(crit_rate: int) -> float:
    match crit_rate:
        case 0:
            return 1 / 16
        case 1:
            return 1 / 8
        case 2:
            return 1 / 2
        case 3 | 4:
            return 1.00
        case _:
            raise ValueError(crit_rate)


def gen7plus_crit_chance(crit_rate: int) -> float:
    match crit_rate:
        case 0:
            return 1 / 24
        case 1:
            return 1 / 8
        case 2:
            return 1 / 2
        case 3 | 4:
            return 1.00
        case _:
            raise ValueError(crit_rate)
