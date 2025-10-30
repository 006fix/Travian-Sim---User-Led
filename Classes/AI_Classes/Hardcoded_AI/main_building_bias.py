import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class MainBuildingBias(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Main_Building_Bias"

    def select_building(self, possible_actions, info_packet):
        main_building_list = []
        other_buildings = []
        fields = []
        for item in possible_actions:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == "building" and item.get("name") == "main_building":
                main_building_list.append(item)
            elif item_type == "building":
                other_buildings.append(item)
            elif item_type == "field":
                fields.append(item)

        if len(main_building_list) > 0:
            choose_from_list = main_building_list
        elif len(other_buildings) > 0:
            choose_from_list = other_buildings
        else:
            choose_from_list = fields

        if len(choose_from_list) == 0:
            return None

        return random.choice(choose_from_list)
