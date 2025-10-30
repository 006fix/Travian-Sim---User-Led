import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class FieldFocus(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Field_Focus"

    def select_building(self, possible_actions, info_packet):
        field_options = []
        for item in possible_actions:
            if isinstance(item, dict) and item.get("type") == "field":
                field_options.append(item)

        if len(field_options) > 0:
            choose_from_list = field_options
        else:
            choose_from_list = possible_actions

        if len(choose_from_list) == 0:
            return None

        chosen_action = random.choice(choose_from_list)
        return chosen_action
