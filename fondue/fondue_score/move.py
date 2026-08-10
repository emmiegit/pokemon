import logging
from collections import defaultdict
from typing import NamedTuple

from .api import MoveInfo, fetch_machine, fetch_move_info
from .crit import get_crit_chance
from .game import GameInfo

TARGET_TYPE_OPPONENT = frozenset(
    {
        "specific-move",
        "opponents-field",
        "random-opponent",
        "all-other-pokemon",
        "selected-pokemon",
        "all-opponents",
        "entire-field",
        "all-pokemon",
    }
)

MoveDamageByType = dict[str, dict[str, float]]

logger = logging.getLogger(__name__)


class MoveCompilationForType(NamedTuple):
    type: str
    damage_total: float
    move_count: int


def move_is_hm(move: MoveInfo, game: GameInfo) -> bool:
    for machine in move["machines"]:
        if machine["version_group"]["name"] != game.version_group:
            # not applicable
            continue

        machine_info = fetch_machine(machine["machine"]["url"])
        if machine_info["item"]["name"].startswith("hm"):
            return True

    return False


def calculate_damage(move: MoveInfo, game: GameInfo) -> float | None:
    logger.info("Calculating damage for move %s (ID %d)", move["name"], move["id"])
    meta = move["meta"]
    power = move["power"]

    # Filter out moves

    if meta is None:
        # Not valid for our purposes
        logger.debug("Skipping move, no metadata")
        return None

    if move["target"]["name"] not in TARGET_TYPE_OPPONENT:
        logger.debug("Skipping move, doesn't target opponents")
        return None

    if move_is_hm(move, game):
        logger.debug("Skipping move, is HM")
        return None

    if power is None:
        logger.debug("Skipping move, status only")
        return None

    if power < 50:
        logger.debug("Skipping move, BP %d < 50", power)
        return None

    # Calculate amortized damage
    damage = float(power)

    # Factor in accuracy
    accuracy = move["accuracy"]
    if accuracy is not None:
        # None means 'always hits'
        damage *= accuracy / 100

    # Critical hit chance and damage
    crit_chance = get_crit_chance(game.generation, meta["crit_rate"])
    damage *= 1.0 + crit_chance

    # Flinch chance
    # TODO

    # Evaluate multi-hit moves
    if meta["min_hits"] is not None and meta["max_hits"] is not None:
        average_hits = (meta["min_hits"] + meta["max_hits"]) / 2
        damage *= average_hits

    # Move priority
    if move["priority"] > 0:
        # Priority moves get a 50% bonus
        damage *= 1.5
    elif move["priority"] < 0:
        # Negative priority gets a 25% penalty
        damage *= 0.75

    return damage


def calculate_damage_by_type(game: GameInfo) -> MoveDamageByType:
    moves_by_type: MoveDamageByType = defaultdict(dict)
    for move_spec in game.all_moves():
        move = fetch_move_info(move_spec["url"])
        move_name = move["name"]
        move_type = move["type"]["name"]
        damage = calculate_damage(move, game)
        if damage is None:
            # Exclude from list
            continue

        moves_by_type[move_type][move_name] = damage
    return moves_by_type


def compile_moves_by_type(moves_by_type: MoveDamageByType) -> list[MoveCompilationForType]:
    logger.debug("Organizing types by total damage from moves...")
    stats_by_type = [
        MoveCompilationForType(
            type=move_type,
            damage_total=sum(moves.values()),
            move_count=len(moves),
        )
        for move_type, moves in moves_by_type.items()
    ]
    stats_by_type.sort(key=lambda stats: stats.damage_total, reverse=True)
    return stats_by_type
