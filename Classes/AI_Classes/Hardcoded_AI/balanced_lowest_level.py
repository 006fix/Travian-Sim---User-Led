import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class BalancedLowestLevel(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Balanced_Lowest_Level"

    def select_building(self, possible_actions, info_packet):
        lowest_level = None
        lowest_list = []
        for item in possible_actions:
            if not isinstance(item, dict):
                continue
            level = item.get("level")
            if level is None:
                continue
            if lowest_level is None or level < lowest_level:
                lowest_level = level
                lowest_list = [item]
            elif level == lowest_level:
                lowest_list.append(item)

        if lowest_list:
            choose_from_list = lowest_list
        else:
            choose_from_list = possible_actions

        if len(choose_from_list) == 0:
            return None
        return random.choice(choose_from_list)
