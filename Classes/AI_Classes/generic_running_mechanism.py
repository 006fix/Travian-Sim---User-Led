import random

import Classes.player as player
from simulation_runner import run_logger
from Classes.AI_Classes.generic_ai_base import GenericAIBase, build_info_packet
from master_controller import game_rules


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

    def _count_jobs(self, job_type):
        """Count outstanding jobs of a given type across all villages."""
        total = 0
        for village in self.villages:
            for job in getattr(village, "currently_upgrading", {}).values():
                if job.get("type") == job_type:
                    total += 1
        return total

    def _log_action_event(self, village, action_type, target_repr, wait_time, reason=None):
        """Common logger wrapper for controller-initiated actions."""
        run_logger.log_action(
            player=self.name,
            village_location=getattr(village, "location", None),
            action_type=action_type,
            target=target_repr,
            wait_time=wait_time,
            reason=reason,
            population=village.population,
            culture_rate=village.culture_points_rate,
            culture_total=village.culture_points_total,
            total_yield=village.total_yield,
            ai_label=self.ai_label,
        )

    def _try_priority_settler_action(self, village, wait_time_list):
        """Apply the controller-level settler/settle heuristic."""
        policy = getattr(game_rules, "SETTLER_POLICY", {})
        if not policy.get("prioritise_settle", True):
            return False

        target_settlers = int(policy.get("train_target", 3))
        required_residence = int(policy.get("residence_level_required", 10))

        settle_points = getattr(self, "settle_points", 0)
        if settle_points >= 1:
            # [ISS-036] Temporary lock: players stop after their first settlement; remove when multi-settlement rules land.
            return False

        pending_trainers = self._count_jobs("train_settler")
        built_settlers = getattr(self, "settlers_built", 0)
        residence_level = 0
        if hasattr(village, "_residence_level"):
            residence_level = village._residence_level()

        needs_more_settlers = built_settlers < target_settlers

        if needs_more_settlers and (built_settlers + pending_trainers) < target_settlers and residence_level >= required_residence:
            wait_time = village.start_train_settler()
            if wait_time:
                self._log_action_event(village, "train_settler", "train_settler", wait_time)
                next_wait = village.next_upgrade_completion()
                if next_wait is not None:
                    wait_time_list.append(next_wait)
                return True
        if needs_more_settlers or pending_trainers > 0:
            return False

        if self._count_jobs("settle") > 0:
            return False

        wait_time = village.start_settle()
        if wait_time:
            self._log_action_event(village, "settle", "settle", wait_time)
            next_wait = village.next_upgrade_completion()
            if next_wait is not None:
                wait_time_list.append(next_wait)
            return True

        return False

    def reset_next_action(self, current_time, wait_duration):
        if wait_duration is not None:
            self.next_action_due_at = current_time + wait_duration
        else:
            #issue - this is hardcoded into the AI as a "wait 20k seconds" element - should be dynamic and
            #controlled at a high level
            # [ISS-033] Align idle wake-ups with periodic_monitor cadence once controller scheduling is refactored.
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

        total_culture = 0.0
        total_culture_rate = 0.0

        for curr_village in self.villages:
            curr_village.culture_points_total += curr_village.culture_points_rate * (local_duration_slept / 3600)
            total_culture += curr_village.culture_points_total
            total_culture_rate += curr_village.culture_points_rate
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

            completed_jobs = curr_village.advance_upgrade_jobs(local_duration_slept)
            for job in completed_jobs:
                location = getattr(curr_village, "location", None)
                owner = getattr(curr_village, "owner", None)
                job_type = job.get("type")
                if job_type == "building":
                    curr_village.building_upgraded(job)
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="building",
                        target=curr_village.describe_job(job),
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        resources=curr_village.stored.copy(),
                        storage_cap=curr_village.storage_cap.copy(),
                        ai_label=self.ai_label,
                        game_time=current_time,
                        settlers_built=getattr(owner, "settlers_built", None),
                        settle_points=getattr(owner, "settle_points", None),
                    )
                elif job_type == "field":
                    curr_village.field_upgraded(job)
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="field",
                        target=curr_village.describe_job(job),
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        resources=curr_village.stored.copy(),
                        storage_cap=curr_village.storage_cap.copy(),
                        ai_label=self.ai_label,
                        game_time=current_time,
                        settlers_built=getattr(owner, "settlers_built", None),
                        settle_points=getattr(owner, "settle_points", None),
                    )
                elif job_type == "train_settler":
                    if owner is not None:
                        owner.settlers_built += 1
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="train_settler",
                        target="train_settler",
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        resources=curr_village.stored.copy(),
                        storage_cap=curr_village.storage_cap.copy(),
                        ai_label=self.ai_label,
                        game_time=current_time,
                        settlers_built=getattr(owner, "settlers_built", None),
                        settle_points=getattr(owner, "settle_points", None),
                    )
                    curr_village.remove_upgrade_job(job.get("id"))
                elif job_type == "settle":
                    if owner is not None and owner.settlers_built >= 3:
                        owner.settlers_built -= 3
                        owner.settle_points += 1
                    # [ISS-032] Settlements should refund the population (crop usage) from the departing settlers.
                    run_logger.log_completion(
                        player=self.name,
                        village_location=location,
                        job_type="settle",
                        target="settle",
                        population=curr_village.population,
                        culture_rate=curr_village.culture_points_rate,
                        culture_total=curr_village.culture_points_total,
                        total_yield=curr_village.total_yield,
                        resources=curr_village.stored.copy(),
                        storage_cap=curr_village.storage_cap.copy(),
                        ai_label=self.ai_label,
                        game_time=current_time,
                        settlers_built=getattr(owner, "settlers_built", None),
                        settle_points=getattr(owner, "settle_points", None),
                    )
                    curr_village.remove_upgrade_job(job.get("id"))
                else:
                    curr_village.remove_upgrade_job(job.get("id"))

            priority_scheduled = self._try_priority_settler_action(curr_village, wait_time_list)
            if priority_scheduled:
                reset_time = True
                continue

            possible_actions = curr_village.possible_buildings()
            merged_list = [item for subset in possible_actions.values() for item in subset]

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

            if chosen_item is None:
                self._log_action_event(
                    curr_village,
                    "idle",
                    None,
                    None,
                    reason="no available upgrades",
                )
            else:
                reset_time = True
                item_type = chosen_item.get("type")
                if item_type == "building":
                    wait_time = curr_village.upgrade_building([chosen_item["slot"], chosen_item["name"]])
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
                self._log_action_event(curr_village, action_label, target_repr, wait_time)

            next_wait = curr_village.next_upgrade_completion()
            if next_wait is not None:
                reset_time = True
                wait_time_list.append(next_wait)

        self.culture_points = total_culture
        self.culture_points_rate = total_culture_rate

        if reset_time and wait_time_list:
            true_wait_time = min(wait_time_list)
            self.reset_next_action(current_time, true_wait_time)
            return true_wait_time

        self.reset_next_action(current_time, None)
        return self.next_action_due_at - current_time
