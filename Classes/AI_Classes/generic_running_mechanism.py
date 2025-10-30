import random

import Classes.player as player
from simulation_runner import run_logger
from Classes.AI_Classes.generic_ai_base import GenericAIBase, build_info_packet


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
        self.ai_label = getattr(self.ai_controller, "name", "Generic Random")

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
            curr_village.culture_points_total += curr_village.culture_points_rate * (local_duration_slept / 3600)
            resources_gained = curr_village.yield_calc()
            for i in range(len(resources_gained)):
                resources_gained[i] *= local_duration_slept
            current_stockpile = curr_village.stored
            current_max = curr_village.storage_cap
            for i in range(len(resources_gained)):
                updated_amount = current_stockpile[i] + resources_gained[i]
                if updated_amount > current_max[i]:
                    current_stockpile[i] = current_max[i]
                elif updated_amount < 0:
                    current_stockpile[i] = 0
                else:
                    current_stockpile[i] = updated_amount
            curr_village.stored = current_stockpile

            if len(curr_village.currently_upgrading) > 0:
                job = curr_village.currently_upgrading[0]
                location = getattr(curr_village, "location", None)
                # [ISS-015] still relying on nested lists; swap to structured job records when queue logic is rewritten.
                if len(job) == 2:
                    curr_village.building_upgraded(job)
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="building",
                        target=str(job),
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        resources=curr_village.stored.copy(),
                        storage_cap=curr_village.storage_cap.copy(),
                        ai_label=self.ai_label,
                    )
                else:
                    curr_village.field_upgraded(job[0])
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="field",
                        target=job[0],
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        resources=curr_village.stored.copy(),
                        storage_cap=curr_village.storage_cap.copy(),
                        ai_label=self.ai_label,
                    )

            possible_actions = curr_village.possible_buildings()
            merged_list = [
                item for subset in possible_actions.values() for item in subset
            ]

            if self.ai_controller is None:
                if merged_list:
                    index = self.rng_holder.randint(0, len(merged_list) - 1)
                    chosen_item = merged_list[index]
                else:
                    chosen_item = None
            else:
                if hasattr(self.ai_controller, "derive_next_action"):
                    chosen_item = self.ai_controller.derive_next_action()
                elif isinstance(self.ai_controller, GenericAIBase) or hasattr(self.ai_controller, "select_building"):
                    info_packet = build_info_packet(
                        player=self,
                        village=curr_village,
                        game_time=current_time,
                        global_last_active=global_last_active,
                    )
                    chosen_item = self.ai_controller.select_building(merged_list, info_packet)
                else:
                    chosen_item = None

            if len(curr_village.currently_upgrading) != 0:
                run_logger.log_action(
                    player=self.name,
                    village_location=getattr(curr_village, "location", None),
                    action_type="queue_blocked",
                    target=None,
                    wait_time=None,
                    reason="queue already busy",
                    population=curr_village.population,
                    culture_rate=curr_village.culture_points_rate,
                    culture_total=curr_village.culture_points_total,
                    total_yield=curr_village.total_yield,
                    ai_label=self.ai_label,
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
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        ai_label=self.ai_label,
                    )
                else:
                    reset_time = True
                    item_type = chosen_item.get("type")
                    if item_type == "building":
                        wait_time = curr_village.upgrade_building(
                            [chosen_item["slot"], chosen_item["name"]]
                        )
                        target_repr = chosen_item["name"]
                        action_label = "upgrade_building"
                    elif item_type == "field":
                        field_id = chosen_item["field_id"]
                        wait_time = curr_village.upgrade_field(field_id)
                        target_repr = field_id
                        action_label = "upgrade_field"
                    else:
                        wait_time = None
                        target_repr = None
                        action_label = "unknown"
                    run_logger.log_action(
                        player=self.name,
                        village_location=getattr(curr_village, "location", None),
                        action_type=action_label,
                        target=target_repr,
                        wait_time=wait_time,
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        ai_label=self.ai_label,
                    )
                    if wait_time is not None:
                        wait_time_list.append(wait_time)

        if reset_time and wait_time_list:
            true_wait_time = min(wait_time_list)
            self.reset_next_action(current_time, true_wait_time)
            return true_wait_time

        self.reset_next_action(current_time, None)
        return self.next_action_due_at - current_time
