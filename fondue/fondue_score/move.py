from .api import fetch_move_info
from .crit import get_crit_chance


def calculate_damage(generation: int, move_url: str) -> float:
    move = fetch_move_info(move_url)
    crit_chance = get_crit_chance(generation, move["meta"]["crit_rate"])
    # TODO
    ...
