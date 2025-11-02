import Classes.base_squares as base_squares
import Base_Data.Building_Data as b_data
import Base_Data.Fields_Data as f_data
import Generic_Functions.generic_functions as gen_func
import random

from master_controller import game_rules

class Village(base_squares.Square):
    def __init__(self, location, type_hab, field_list_dict, owner, type_square='village'):
        super().__init__(location)
        self.location = location
        self.interactable = True
        self.type_hab = type_hab
        self.fields = field_list_dict
        self.type_square = type_square
        self.owner = owner
        self.buildings = {0: '', 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '',
                    9: '', 10: '', 11: '', 12: '', 13: '', 14: '', 15: '', 16: '',
                    17: '', 18: '', 19: '', 20: '', 21: '', 22: ''}
        #structure of the below - reference key for buildings_dict lookup, level, upgradeable bool.
        self.buildings[0] = ['main_building', 1, True]

        self.available_buildings = set(b_data.building_dict.keys())
        for slot_info in self.buildings.values():
            if isinstance(slot_info, list) and len(slot_info) > 0:
                self.available_buildings.discard(slot_info[0])

        #default instantiation values
        self.storage_cap = [800, 800, 800, 800]
        self.stored = [800,800,800,800]
        self.currently_upgrading = {}
        self._upgrade_job_sequence = 0
        self.population = 0
        self.culture_points_rate = 0.0
        self.culture_points_total = 0.0
        self.total_yield = 0.0
        self._recalculate_population_and_culture()

    #function to calculate storage, ignoring existence of the premade 800 setup for empty vils
    def calculate_storage(self):
        warehouse_storage = 0
        granary_storage = 0
        for key in self.buildings:
            holder = self.buildings[key]
            #check if its empty
            if len(holder) > 0:
                if 'warehouse' in holder[0]:
                    level = holder[1]
                    storage = b_data.building_dict['warehouse'][level][4]
                    warehouse_storage += storage
                if 'granary' in holder[0]:
                    level = holder[1]
                    storage = b_data.building_dict['granary'][level][4]
                    granary_storage += storage
            #extra section to stop it setting back to 0 if buildings destroyed
        self.storage_cap = [max(warehouse_storage, 800),
                            max(warehouse_storage, 800),
                            max(warehouse_storage, 800),
                            max(granary_storage, 800)]

    #fairly basic function to calculate yield, has some innefficiencies noted below
    #returns per second yields, which then get multiplied out by time elapsed
    def yield_calc(self):
        wood_yield = 0
        clay_yield = 0
        iron_yield = 0
        crop_yield = 0
        for key3, field_obj in self.fields.items():
            if 'Wood' in key3:
                wood_yield += field_obj.field_yield
            if 'Clay' in key3:
                clay_yield += field_obj.field_yield
            if 'Iron' in key3:
                iron_yield += field_obj.field_yield
            if 'Crop' in key3:
                crop_yield += field_obj.field_yield

        wood_bonus = 0.0
        clay_bonus = 0.0
        iron_bonus = 0.0
        crop_bonus = 0.0
        for building in self.buildings.values():
            if not building or len(building) <= 1:
                continue
            name, level, _ = building
            if name in ('sawmill', 'brickyard', 'iron_foundry', 'grain_mill', 'bakery'):
                entry = b_data.building_dict.get(name, {}).get(level)
                if entry is None:
                    continue
                bonus = entry[4] or 0.0
                if name == 'sawmill':
                    wood_bonus += bonus
                elif name == 'brickyard':
                    clay_bonus += bonus
                elif name == 'iron_foundry':
                    iron_bonus += bonus
                else:
                    crop_bonus += bonus

        wood_yield *= (1.0 + wood_bonus)
        clay_yield *= (1.0 + clay_bonus)
        iron_yield *= (1.0 + iron_bonus)
        crop_yield *= (1.0 + crop_bonus)

        wood_yield = wood_yield / 3600
        clay_yield = clay_yield / 3600
        iron_yield = iron_yield / 3600
        net_crop = crop_yield - self.population
        crop_yield = net_crop / 3600

        yields = [wood_yield, clay_yield, iron_yield, crop_yield]
        return yields
    
    
    def possible_buildings(self):
        #modified to dictionary variant to store both in one item
        possible_buildings = {'buildings': [], 'fields': []}
        crop_yield_per_hour = self.yield_calc()[3] * 3600
        for key in self.buildings:
            holdval = self.buildings[key]
            #if buildings exist that can be built
            if len(holdval) > 1:
                holdval_level = holdval[1]
                #if upgradeable
                if holdval[2] == True:
                    keyval = holdval[0]
                    entry, _ = self._get_building_entry(keyval, holdval_level)
                    next_entry, _ = self._get_building_entry(keyval, holdval_level + 1)
                    if next_entry is None:
                        continue
                    previous_pop = entry[2] if entry is not None else 0
                    pop_delta = next_entry[2] - previous_pop
                    if crop_yield_per_hour <= 0 or pop_delta >= crop_yield_per_hour:
                        continue
                    upgrade_cost = next_entry[0]
                    #default to assuming enough res, then make false if not true
                    enough_res = True
                    for i in range(4):
                        if upgrade_cost[i] > self.stored[i]:
                            enough_res = False
                    if enough_res:
                        final_value = {
                            'type': 'building',
                            'slot': key,
                            'name': holdval[0],
                            'level': holdval_level,
                        }
                        dictval = possible_buildings['buildings']
                        dictval.append(final_value)
        empty_slots = [slot for slot, value in self.buildings.items() if not value]  # [ISS-023] allow maxed storage buildings to bypass this guard later
        if empty_slots and self.available_buildings:
            for slot in empty_slots:
                for building_name in sorted(self.available_buildings):
                    level_data = b_data.building_dict.get(building_name, {}).get(1)
                    if level_data is None:
                        continue
                    upgrade_cost = level_data[0]
                    if all(self.stored[i] >= upgrade_cost[i] for i in range(4)):
                        possible_buildings['buildings'].append(
                            {
                                'type': 'building',
                                'slot': slot,
                                'name': building_name,
                                'level': 0,
                                'new_build': True,
                            }
                        )
        for key in self.fields:
            holdval = self.fields[key]
            holdval_level = holdval.level
            key2 = key[:4]
            if holdval.upgradeable is True:
                current_entry = f_data.field_dict[key2][holdval_level]
                next_entry = f_data.field_dict[key2].get(holdval_level + 1)
                if next_entry is None:
                    continue
                pop_delta = next_entry[2] - current_entry[2]
                if key2 != 'Crop':
                    if crop_yield_per_hour <= 0 or pop_delta >= crop_yield_per_hour:
                        continue
                upgrade_cost = f_data.field_dict[key2][holdval_level][0]
                enough_res = True
                for i in range(4):
                    if upgrade_cost[i] > self.stored[i]:
                        enough_res = False
                if enough_res:
                    final_value = {
                        'type': 'field',
                        'field_id': key,
                        'resource': key2,
                        'level': holdval_level,
                    }
                    dictval = possible_buildings['fields']
                    dictval.append(final_value)
        return possible_buildings   
    
    def upgrade_building(self, upgrade_target):
        building_dict_key = upgrade_target[0]
        building_data_key = upgrade_target[1]
        relevant_target = self.buildings[building_dict_key]
        is_new_build = not relevant_target
        if is_new_build:
            current_level = 0
            upgradeable_check = True
        else:
            current_level = relevant_target[1]
            upgradeable_check = relevant_target[2]
        if upgradeable_check is not True:
            raise ValueError("You appear to have attempted to upgrade a building that cannot be upgraded :(")
        target_level = current_level + 1
        target_entry, _ = self._get_building_entry(building_data_key, target_level)
        if target_entry is None:
            raise ValueError(f"Building data missing for {building_data_key} at level {target_level}")
        upgrade_cost = target_entry[0]
        upgrade_time = target_entry[3]

        speed_modifier = self._main_building_speed_modifier()
        true_upgrade_time = gen_func.sec_val(upgrade_time)
        true_upgrade_time = max(1, int(round(true_upgrade_time * speed_modifier)))

        for i in range(4):
            self.stored[i] -= upgrade_cost[i]

        if is_new_build:
            self.buildings[building_dict_key] = [building_data_key, 0, True]
            self.available_buildings.discard(building_data_key)

        sleep_duration = true_upgrade_time
        job_payload = {
            'slot': building_dict_key,
            'building': building_data_key,
            'target_level': target_level,
        }
        self._register_upgrade_job('building', job_payload, sleep_duration)
        return sleep_duration

    def _residence_level(self):
        for data in self.buildings.values():
            if data and len(data) > 1 and data[0] == 'residence':
                return data[1]
        return 0

    def start_train_settler(self):
        if self._residence_level() < 10:
            raise ValueError("Residence level 10 required to train settlers.")
        cost = game_rules.SETTLER_COST
        if any(self.stored[i] < cost[i] for i in range(4)):
            return None
        for i in range(4):
            self.stored[i] -= cost[i]
        duration = gen_func.sec_val(game_rules.SETTLER_TIME)
        payload = {'village': getattr(self, "location", None)}
        self._register_upgrade_job('train_settler', payload, duration)
        return duration

    def start_settle(self):
        owner = getattr(self, "owner", None)
        if owner is None or getattr(owner, "settlers_built", 0) < 3:
            return None
        if owner.culture_points < game_rules.CP_THRESHOLD:
            return None
        cost = game_rules.SETTLE_COST
        if any(self.stored[i] < cost[i] for i in range(4)):
            return None
        for i in range(4):
            self.stored[i] -= cost[i]
        duration = gen_func.sec_val(game_rules.SETTLE_TIME)
        payload = {'village': getattr(self, "location", None)}
        self._register_upgrade_job('settle', payload, duration)
        return duration
    
    def upgrade_field(self, upgrade_target):

        #find fields within self.fields, and get key, level, upgradeable
        field_data = self.fields[upgrade_target]
        field_dict_key = upgrade_target[:4]
        current_level = field_data.level
        upgradeable_check = field_data.upgradeable

        #this is fine for now, as i'm happy for it to break
        #however, this is a future issue and candidate for logging
        if upgradeable_check != True:
            print(f"you are upgrading {upgrade_target}")
            raise ValueError("You appear to have attempted to upgrade a field that cannot be upgraded :(")

        #get upgrade cost and upgrade time
        upgrade_cost = f_data.field_dict[field_dict_key][current_level][0]
        upgrade_time = f_data.field_dict[field_dict_key][current_level][3]
        speed_modifier = self._main_building_speed_modifier()
        true_upgrade_time = gen_func.sec_val(upgrade_time)
        true_upgrade_time = max(1, int(round(true_upgrade_time * speed_modifier)))

        #remove cost of everything used for upgrades
        hold_vals = self.stored
        for i in range(len(hold_vals)):
            hold_vals[i] -= upgrade_cost[i]
        self.stored = hold_vals

        sleep_duration = true_upgrade_time
        job_payload = {
            'field_id': upgrade_target,
            'resource_type': field_dict_key,
            'target_level': current_level + 1,
        }
        self._register_upgrade_job('field', job_payload, sleep_duration)
        return sleep_duration


    def building_upgraded(self, job):

        if not isinstance(job, dict):
            raise TypeError("building_upgraded expects a job dictionary payload")

        payload = job.get('payload', {})
        building_dict_key = payload.get('slot')
        building_data_key = payload.get('building')
        if building_dict_key is None or building_data_key is None:
            raise ValueError("Incomplete job payload for building upgrade completion")

        #same start code as above
        #built and designed for the 2 key building logic in possible_buildings
        relevant_target = self.buildings[building_dict_key]
        current_level = relevant_target[1]
        upgradeable_check = relevant_target[2]

        #this is imperfect, but should work fine - you can't ugprade if its not upgradeable
        #so not risk of overflow error
        #however, this is still an extant issue, as it uses the false flag.
        level_plusone = current_level + 1
        old_entry, _ = self._get_building_entry(building_data_key, current_level)
        if old_entry is None:
            old_entry = [[0, 0, 0, 0], 0, 0, [0, 0, 0], 0]
        new_entry, upgrade_possible = self._get_building_entry(building_data_key, level_plusone)
        if new_entry is None:
            raise ValueError(f"Building data missing for {building_data_key} at level {level_plusone}")

        #applying the new values derived above for the upgraded building
        old_vals = self.buildings[building_dict_key]
        old_vals[2] = upgrade_possible
        old_vals[1] = level_plusone
        #potentially not needed, superflous step
        self.buildings[building_dict_key] = old_vals
        pop_delta = new_entry[2] - old_entry[2]
        self.population += pop_delta
        self.culture_points_rate += new_entry[1] - old_entry[1]
        #buildings do not directly add yield in the current dataset, so only the population delta applies
        self.total_yield -= pop_delta

        if building_data_key in ("warehouse", "granary"):
            self.calculate_storage()

        #remove only the completed job
        self.remove_upgrade_job(job.get('id'))

        #nothing returned, merely modifies values in place
    
    def field_upgraded(self, job):

        if not isinstance(job, dict):
            raise TypeError("field_upgraded expects a job dictionary payload")

        payload = job.get('payload', {})
        upgrade_target = payload.get('field_id')
        if upgrade_target is None:
            raise ValueError("Incomplete job payload for field upgrade completion")

        field_data = self.fields[upgrade_target]
        field_dict_key = upgrade_target[:4]

        current_level = field_data.level

        #used to check if the new building is upgradeable
        # ISSUE : for fields in non capital, this will eventually need to cap at 10 in some way
        level_plusone = current_level + 1
        still_upgradeable = f_data.field_dict[field_dict_key][level_plusone][0]
        if still_upgradeable[0] == False:
            upgrade_possible = False
        else:
            upgrade_possible = True

        # used to update the villages building list with the new level and upgradeability
        field_data.level = level_plusone
        field_data.upgradeable = upgrade_possible
        old_entry = f_data.field_dict[field_dict_key][current_level]
        new_entry = f_data.field_dict[field_dict_key][level_plusone]
        field_data.upgrade_cost = new_entry[0]
        field_data.field_yield = new_entry[4]
        field_data.cp = new_entry[1]
        field_data.pop = new_entry[2]
        field_data.upgrade_time = gen_func.sec_val(new_entry[3])
        pop_delta = new_entry[2] - old_entry[2]
        yield_delta = new_entry[4] - old_entry[4]
        self.population += pop_delta
        self.culture_points_rate += new_entry[1] - old_entry[1]
        self.total_yield += yield_delta - pop_delta

        #remove only the completed job
        self.remove_upgrade_job(job.get('id'))

        #nothing returned, merely modifies values in place


    def _recalculate_population_and_culture(self):
        total_pop = 0
        total_cp_rate = 0.0
        total_field_yield = 0.0
        for field_id, field_obj in self.fields.items():
            prefix = field_id[:4]
            entry = f_data.field_dict[prefix][field_obj.level]
            total_pop += entry[2]
            total_cp_rate += entry[1]
            total_field_yield += entry[4]
        for building in self.buildings.values():
            if building and len(building) > 1:
                building_key = building[0]
                level = building[1]
                entry = b_data.building_dict[building_key][level]
                total_pop += entry[2]
                total_cp_rate += entry[1]
        self.population = total_pop
        self.culture_points_rate = float(total_cp_rate)
        self.total_yield = float(total_field_yield - total_pop)

    def _main_building_speed_modifier(self):
        """Return the current main building speed modifier."""
        main_building = self.buildings.get(0)
        if main_building and len(main_building) > 1:
            current_level = main_building[1]
            try:
                modifier = b_data.building_dict['main_building'][current_level][4]
                if isinstance(modifier, (int, float)):
                    return modifier
            except KeyError:
                pass
        return 5  # [ISS-034] relies on the main building remaining in slot 0; revisit when slots become dynamic.

    def _get_building_entry(self, building_name, level):
        """Safely fetch building data and indicate if further upgrades are available."""
        table = b_data.building_dict.get(building_name)
        if table is None:
            return None, False
        entry = table.get(level)
        next_entry = table.get(level + 1) if entry is not None else None
        if entry is None:
            # level 0 (or missing) entries are treated as having no data but may still be upgradeable.
            if level == 0 and table.get(1) is not None:
                return None, True
            return None, False
        upgradeable = next_entry is not None
        return entry, upgradeable

    def _register_upgrade_job(self, job_type, payload, duration):
        """Add a new job to the upgrade queue."""
        self._upgrade_job_sequence += 1
        job_id = self._upgrade_job_sequence
        job = {
            'id': job_id,
            'type': job_type,
            'payload': payload,
            'time_remaining': int(duration),
            'initial_duration': int(duration),
        }
        self.currently_upgrading[job_id] = job
        return job

    def advance_upgrade_jobs(self, elapsed):
        """Reduce remaining time on all jobs and return any that completed."""
        if elapsed <= 0 or not self.currently_upgrading:
            return []
        completed = []
        for job in list(self.currently_upgrading.values()):
            remaining = job.get('time_remaining', 0)
            updated = max(0, int(round(remaining - elapsed)))
            job['time_remaining'] = updated
            if updated <= 0:
                completed.append(job)
        return completed

    def describe_job(self, job):
        """Return a human-readable label for logging purposes."""
        if not isinstance(job, dict):
            return str(job)
        job_type = job.get('type')
        payload = job.get('payload', {})
        if job_type == 'building':
            slot = payload.get('slot')
            name = payload.get('building')
            target_level = payload.get('target_level')
            if slot is not None and name is not None:
                return f"{name}@{slot} -> {target_level}"
            return name or f"building_slot_{slot}"
        if job_type == 'field':
            field_id = payload.get('field_id')
            target_level = payload.get('target_level')
            if field_id is not None:
                return f"{field_id} -> {target_level}"
        return "unknown_job"

    def remove_upgrade_job(self, job_id):
        """Remove a job from the queue if it exists."""
        self.currently_upgrading.pop(job_id, None)

    def next_upgrade_completion(self):
        """Return the smallest positive time remaining among queued jobs."""
        if not self.currently_upgrading:
            return None
        remaining_times = [job['time_remaining'] for job in self.currently_upgrading.values() if job['time_remaining'] > 0]
        if not remaining_times:
            return 0
        return min(remaining_times)
