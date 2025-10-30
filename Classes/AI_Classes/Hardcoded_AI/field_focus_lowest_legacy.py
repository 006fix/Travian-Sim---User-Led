import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class FieldFocusLowestLegacy(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Field_Focus_Lowest_Legacy"

    def select_building(self, possible_actions, info_packet):
        field_subset = []
        building_subset = []
        for item in possible_actions:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == "field":
                field_subset.append(item)
            elif item_type == "building":
                building_subset.append(item)

        if field_subset:
            lowest_level = None
            lowest_list = []
            for item in field_subset:
                level = item.get("level")
                if lowest_level is None or (level is not None and level < lowest_level):
                    lowest_level = level
                    lowest_list = [item]
                elif level == lowest_level:
                    lowest_list.append(item)
            choose_from_list = lowest_list if lowest_list else field_subset
        elif building_subset:
            lowest_level = None
            lowest_list = []
            for item in building_subset:
                level = item.get("level")
                if lowest_level is None or (level is not None and level < lowest_level):
                    lowest_level = level
                    lowest_list = [item]
                elif level == lowest_level:
                    lowest_list.append(item)
            choose_from_list = lowest_list if lowest_list else building_subset
        else:
            choose_from_list = possible_actions

        if not choose_from_list:
            return None
        return random.choice(choose_from_list)
