import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


SUPPORT_BUILDINGS = {
    "smithy",
    "academy",
    "barracks",
    "stable",
    "workshop",
    "marketplace",
    "residence",
    "palace",
    "town_hall",
    "hero_mansion",
    "blacksmith",
    "armoury",
}


class StorageSupportBlend(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Storage_Support_Blend"

    def select_building(self, possible_actions, info_packet):
        warehouses = []
        granaries = []
        support = []
        other_buildings = []
        fields = []

        for item in possible_actions:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            name = item.get("name")
            if item_type == "building" and name == "warehouse":
                warehouses.append(item)
            elif item_type == "building" and name == "granary":
                granaries.append(item)
            elif item_type == "building" and name in SUPPORT_BUILDINGS:
                support.append(item)
            elif item_type == "building":
                other_buildings.append(item)
            elif item_type == "field":
                fields.append(item)

        if warehouses:
            choose_from_list = warehouses
        elif granaries:
            choose_from_list = granaries
        elif support:
            choose_from_list = support
        elif other_buildings:
            choose_from_list = other_buildings
        else:
            choose_from_list = fields

        if len(choose_from_list) == 0:
            return None
        return random.choice(choose_from_list)
