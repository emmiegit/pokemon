from collections import defaultdict

from .api import MoveInfo, fetch_all_moves, fetch_move_info
from .crit import get_crit_chance

MoveDamageByType = dict[str, dict[str, float]]


def calculate_damage(generation: int, move: MoveInfo) -> float | None:
    power = move["power"]

    # Skip status moves
    if power is None:
        return None

    # Skip moves less than 50 BP
    if power < 50:
        return None

    crit_chance = get_crit_chance(generation, move["meta"]["crit_rate"])
    is_priority = move["priority"] > 0  # TODO what about negative prio

    # TODO
    ...
    return power * (1.0 + crit_chance)


def compile_moves_by_type(generation: int) -> MoveDamageByType:
    moves_by_type: MoveDamageByType = defaultdict(dict)
    for move_spec in fetch_all_moves(generation):
        move = fetch_move_info(move_spec["url"])
        move_name = move["name"]
        move_type = move["type"]["name"]
        damage = calculate_damage(generation, move)
        if damage is None:
            # Exclude from list
            continue

        moves_by_type[move_type][move_name] = damage
    return moves_by_type
