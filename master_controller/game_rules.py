"""Centralised game configuration for settler mechanics and future balancing tweaks."""

from __future__ import annotations

from math import floor
from typing import List

SETTLER_COST: List[int] = [4600, 4200, 5800, 4400]
SETTLER_POP: int = 1
SETTLER_TIME: List[int] = [7, 28, 20]  # hours, minutes, seconds

SETTLE_COST: List[int] = [750, 750, 750, 750]
SETTLE_TIME: List[int] = [0, 0, 1]

CP_THRESHOLD: int = 2000

SETTLER_POLICY = {
    "train_target": 3,
    "residence_level_required": 10,
    "prioritise_settle": True,
}


def target_settles(num_players: int) -> int:
    """Return the global settle goal for the current run."""
    return max(1, round(num_players / 10))
