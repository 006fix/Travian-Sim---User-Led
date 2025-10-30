import random

from Classes.AI_Classes.generic_ai_base import GenericAIBase


class _ResourceSpecialist(GenericAIBase):
    def __init__(self, owning_player, resource_name, display_name):
        super().__init__(owning_player)
        self.target_resource = resource_name
        self.name = display_name

    def select_building(self, possible_actions, info_packet):
        preferred_fields = []
        other_fields = []
        buildings = []
        for item in possible_actions:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == "field":
                if item.get("resource") == self.target_resource:
                    preferred_fields.append(item)
                else:
                    other_fields.append(item)
            elif item_type == "building":
                buildings.append(item)

        if len(preferred_fields) > 0:
            choose_from_list = preferred_fields
        elif len(other_fields) > 0:
            choose_from_list = other_fields
        else:
            choose_from_list = buildings

        if len(choose_from_list) == 0:
            return None
        return random.choice(choose_from_list)


class CropHoarder(_ResourceSpecialist):
    def __init__(self, owning_player):
        super().__init__(owning_player, "Crop", "Resource_Specialist_Crop")


class WoodWorker(_ResourceSpecialist):
    def __init__(self, owning_player):
        super().__init__(owning_player, "Wood", "Resource_Specialist_Wood")


class ClayCrafter(_ResourceSpecialist):
    def __init__(self, owning_player):
        super().__init__(owning_player, "Clay", "Resource_Specialist_Clay")


class IronMiner(_ResourceSpecialist):
    def __init__(self, owning_player):
        super().__init__(owning_player, "Iron", "Resource_Specialist_Iron")
