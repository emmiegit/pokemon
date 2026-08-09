from .api import fetch_move_info
from .crit import get_crit_chance


def calculate_damage(generation: int, move_url: str) -> float | None:
    move = fetch_move_info(move_url)
    power = move["power"]

    # Skip moves less than 50 BP
    if power < 50:
        return None

    crit_chance = get_crit_chance(generation, move["meta"]["crit_rate"])
    is_priority = move["priority"] > 0  # TODO what about negative prio

    # TODO
    ...
    return power * (1.0 + crit_chance)
