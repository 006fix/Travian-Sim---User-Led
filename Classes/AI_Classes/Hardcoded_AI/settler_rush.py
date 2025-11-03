import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class SettlerRush(GenericAIBase):
    """
    Heuristic tuned for early settling:
    - Push all resource fields to level 7, always upgrading the lowest-level field first.
    - When fields are at target level, invest in storage (warehouse/granary) up to level 9.
    - Only upgrades main building and residence up to level 10.
    - Ignores every other building type (and leaves settler jobs to the controller).
    """

    TARGET_FIELD_LEVEL = 7
    STORAGE_NAMES = {"warehouse", "granary"}
    ALLOWED_BUILDINGS = {"warehouse", "granary", "residence", "main_building"}
    MAX_LEVELS = {
        "warehouse": 9,
        "granary": 9,
        "main_building": 10,
        "residence": 10,
    }

    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Settler_Rush"

    def select_building(self, possible_actions, info_packet):
        fields = []
        storage_candidates = []
        other_allowed = []

        for item in possible_actions:
            if not isinstance(item, dict):
                continue

            item_type = item.get("type")
            if item_type == "field":
                level = item.get("level", 0)
                if level < self.TARGET_FIELD_LEVEL:
                    fields.append(item)
                continue

            if item_type != "building":
                continue

            name = item.get("name")
            if name not in self.ALLOWED_BUILDINGS:
                continue

            current_level = item.get("level", 0)
            if item.get("new_build"):
                current_level = 0
            target_level = current_level + 1
            max_level = self.MAX_LEVELS.get(name)
            if max_level is not None and target_level > max_level:
                continue

            if name in self.STORAGE_NAMES:
                storage_candidates.append(item)
            else:
                other_allowed.append(item)

        if fields:
            lowest_level = min(item.get("level", 0) for item in fields)
            lowest_fields = [item for item in fields if item.get("level", 0) == lowest_level]
            return self._choose(lowest_fields)

        if storage_candidates:
            return self._choose(storage_candidates)

        if other_allowed:
            return self._choose(other_allowed)

        return None

    def _choose(self, options):
        if not options:
            return None
        rng = getattr(self.owning_player, "rng_holder", None)
        if rng is None:
            return random.choice(options)
        return rng.choice(options)
