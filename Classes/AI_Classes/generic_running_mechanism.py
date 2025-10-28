import random

import Classes.player as player
from simulation_runner import run_logger


class base_controller(player.Player):
    def __init__(
        self,
        name,
        quadrant,
        race,
        ai_controller,
        population=0,
        attack_points=0,
        defence_points=0,
        raid_points=0,
        culture_points=0,
        villages=None,
        AI_type="generic",
        rng_holder=None,
    ):
        if villages is None:
            villages = []
        super().__init__(
            name,
            quadrant,
            race,
            ai_controller,
            population=population,
            attack_points=attack_points,
            defence_points=defence_points,
            raid_points=raid_points,
            culture_points=culture_points,
        )
        self.villages = villages
        self.rng_holder = rng_holder if rng_holder is not None else random
        self.next_action_due_at = 0

    def reset_next_action(self, current_time, wait_duration):
        if wait_duration is not None:
            self.next_action_due_at = current_time + wait_duration
        else:
            #issue - this is hardcoded into the AI as a "wait 20k seconds" element - should be dynamic and
            #controlled at a high level
            self.next_action_due_at = current_time + 20000
        #issue - this function doesn't return anything, but it should absolutely log stuff

    def will_i_act(self, current_time, global_last_active):
        remaining = self.next_action_due_at - current_time
        if remaining > 0:
            return remaining

        local_duration_slept = current_time - self.Last_Active
        self.Last_Active = current_time

        wait_time_list = []
        reset_time = False

        for curr_village in self.villages:
            resources_gained = curr_village.yield_calc()
            for i in range(len(resources_gained)):
                resources_gained[i] *= local_duration_slept
            current_stockpile = curr_village.stored
            current_max = curr_village.storage_cap
            for i in range(len(resources_gained)):
                if resources_gained[i] + current_stockpile[i] > current_max[i]:
                    current_stockpile[i] = current_max[i]
                else:
                    current_stockpile[i] = current_stockpile[i] + resources_gained[i]
            curr_village.stored = current_stockpile

            if len(curr_village.currently_upgrading) > 0:
                job = curr_village.currently_upgrading[0]
                location = getattr(curr_village, "location", None)
                # [ISS-015] still relying on nested lists; swap to structured job records when queue logic is rewritten.
                if len(job) == 2:
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="building",
                        target=str(job),
                    )
                    curr_village.building_upgraded(job)
                else:
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="field",
                        target=job[0],
                    )
                    curr_village.field_upgraded(job[0])

            possible_actions = curr_village.possible_buildings()

            if self.ai_controller is None:
                merged_list = []
                origin_list = []
                for key in possible_actions:
                    hold_list = possible_actions[key]
                    for item in hold_list:
                        merged_list.append(item)
                        origin_list.append(key)

                if len(merged_list) == 0:
                    chosen_item = None
                    chosen_origin = None
                else:
                    index = self.rng_holder.randint(0, len(merged_list) - 1)
                    chosen_item = merged_list[index]
                    chosen_origin = origin_list[index]
            else:
                chosen_item, chosen_origin = self.ai_controller.derive_next_action()

            if len(curr_village.currently_upgrading) != 0:
                run_logger.log_action(
                    player=self.name,
                    village_location=getattr(curr_village, "location", None),
                    action_type="queue_blocked",
                    target=None,
                    wait_time=None,
                    reason="queue already busy",
                )
                raise ValueError("I have tried to initiate an upgrade, but I'm already upgrading something - why?")
            else:
                if chosen_item is None:
                    run_logger.log_action(
                        player=self.name,
                        village_location=getattr(curr_village, "location", None),
                        action_type="idle",
                        target=None,
                        wait_time=None,
                        reason="no available upgrades",
                    )
                else:
                    reset_time = True
                    if chosen_origin == "buildings":
                        wait_time = curr_village.upgrade_building(chosen_item)
                        target_repr = str(chosen_item)
                    elif chosen_origin == "fields":
                        wait_time = curr_village.upgrade_field(chosen_item[0])
                        target_repr = chosen_item[0]
                    else:
                        wait_time = None
                        target_repr = None
                    run_logger.log_action(
                        player=self.name,
                        village_location=getattr(curr_village, "location", None),
                        action_type=f"upgrade_{chosen_origin.rstrip('s')}" if chosen_origin else "unknown",
                        target=target_repr,
                        wait_time=wait_time,
                    )
                    if wait_time is not None:
                        wait_time_list.append(wait_time)

        if reset_time and wait_time_list:
            true_wait_time = min(wait_time_list)
            self.reset_next_action(current_time, true_wait_time)
            return true_wait_time

        self.reset_next_action(current_time, None)
        return self.next_action_due_at - current_time
