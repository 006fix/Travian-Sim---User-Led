"""
Simple base class for Travian AI controllers.

This is intentionally bare-bones so new agents can be written with the
same style as the original hard-coded AIs.  The controller will hand the
AI a list of possible actions plus an optional info packet (player,
village, game timers, etc.).  Sub-classes can decide what to do with
that data and simply return a choice from the list or ``None`` to skip.
"""


class GenericAIBase:
    def __init__(self, owning_player):
        self.owning_player = owning_player
        self.name = "Generic_AI_Base"

    def reset(self):
        """Hook for clearing any cached data before a fresh run."""
        return

    def select_building(self, possible_actions, info_packet):
        """
        Decide which upgrade to take from the supplied options.

        :param possible_actions: list of items emitted by
                                 ``Village.possible_buildings()``.
        :param info_packet: dictionary or object that holds any extra
                            state the controller wants to share
                            (player, village, timers, etc.).
        :return: chosen item from possible_actions or ``None`` when the
                 AI wants to stay idle.
        """
        return None


def build_info_packet(player, village, game_time, global_last_active):
    """
    Helper to assemble a plain dictionary that mirrors the arguments the
    controller currently sends into hard-coded AIs.  Agents can mutate
    or ignore it without worrying about strict typing.
    """
    return {
        "player": player,
        "village": village,
        "game_time": game_time,
        "global_last_active": global_last_active,
        "settlers_built": getattr(player, "settlers_built", 0),
        "settle_points": getattr(player, "settle_points", 0),
    }
