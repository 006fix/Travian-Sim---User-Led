import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class StorageFirst(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Storage_First"

    def select_building(self, possible_actions, info_packet):
        warehouse_list = []
        granary_list = []
        other_buildings = []
        fields = []
        for item in possible_actions:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            name = item.get("name")
            if item_type == "building" and name == "warehouse":
                warehouse_list.append(item)
            elif item_type == "building" and name == "granary":
                granary_list.append(item)
            elif item_type == "building":
                other_buildings.append(item)
            elif item_type == "field":
                fields.append(item)

        if len(warehouse_list) > 0:
            choose_from_list = warehouse_list
        elif len(granary_list) > 0:
            choose_from_list = granary_list
        elif len(other_buildings) > 0:
            choose_from_list = other_buildings
        else:
            choose_from_list = fields

        if len(choose_from_list) == 0:
            return None

        return random.choice(choose_from_list)
