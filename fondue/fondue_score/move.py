from collections import defaultdict
import logging
from typing import NamedTuple

from .api import MoveInfo, fetch_all_moves, fetch_move_info
from .crit import get_crit_chance

MoveDamageByType = dict[str, dict[str, float]]

logger = logging.getLogger(__name__)


class MoveStatsForType(NamedTuple):
    type: str
    damage_total: float
    move_count: int


def calculate_damage(generation: int, move: MoveInfo) -> float | None:
    logger.info("Calculating damage for move %s (ID %d)", move["name"], move["id"])
    power = move["power"]

    # Not valid for our purposes
    if move["meta"] is None:
        logger.debug("Skipping move, no metadata")
        return None

    # Skip status moves
    if power is None:
        logger.debug("Skipping move, status only")
        return None

    # Skip moves less than 50 BP
    if power < 50:
        logger.debug("Skipping move, BP %d < 50", power)
        return None

    # Calculate amortized damage
    damage = power

    # Critical hit chance and damage
    crit_chance = get_crit_chance(generation, move["meta"]["crit_rate"])
    damage *= 1.0 + crit_chance

    # TODO remaining modifications
    is_priority = move["priority"] > 0  # TODO what about negative prio

    return damage


def calculate_damage_by_type(generation: int) -> MoveDamageByType:
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


def compile_moves_by_type(generation: int) -> list[MoveStatsForType]:
    moves_by_type = calculate_damage_by_type(generation)
    logger.debug("Organizing types by total damage from moves...")
    stats_by_type = [
        MoveStatsForType(
            type=move_type,
            damage_total=sum(moves.values()),
            move_count=len(moves),
        )
        for move_type, moves in moves_by_type.items()
    ]
    stats_by_type.sort(key=lambda stats: stats.damage_total, reverse=True)
    return stats_by_type
