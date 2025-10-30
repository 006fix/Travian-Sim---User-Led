import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class BuildingFocus(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Building_Focus"

    def select_building(self, possible_actions, info_packet):
        building_options = []
        for item in possible_actions:
            if isinstance(item, dict) and item.get("type") == "building":
                building_options.append(item)

        if len(building_options) > 0:
            choose_from_list = building_options
        else:
            choose_from_list = possible_actions

        if len(choose_from_list) == 0:
            return None

        chosen_action = random.choice(choose_from_list)
        return chosen_action
