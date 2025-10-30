import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class FieldFocusLowest(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Field_Focus_Lowest"

    def select_building(self, possible_actions, info_packet):
        field_subset = []
        for item in possible_actions:
            if isinstance(item, dict) and item.get("type") == "field":
                field_subset.append(item)

        if len(field_subset) == 0:
            choose_from_list = possible_actions
        else:
            lowest_level = None
            lowest_list = []
            for item in field_subset:
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
                choose_from_list = field_subset

        if len(choose_from_list) == 0:
            return None

        return random.choice(choose_from_list)
