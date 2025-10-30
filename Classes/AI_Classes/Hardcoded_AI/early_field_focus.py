import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class EarlyFieldFocus(GenericAIBase):
    def __init__(self, owning_player):
        super().__init__(owning_player)
        self.name = "Early_Field_Focus"

    def select_building(self, possible_actions, info_packet):
        fields = []
        for item in possible_actions:
            if isinstance(item, dict) and item.get("type") == "field":
                fields.append(item)

        if len(fields) == 0:
            choose_from_list = possible_actions
        else:
            below_five = []
            for item in fields:
                level = item.get("level")
                if level is not None and level < 5:
                    below_five.append(item)
            if below_five:
                choose_from_list = below_five
            else:
                choose_from_list = fields

        if len(choose_from_list) == 0:
            return None

        return random.choice(choose_from_list)
