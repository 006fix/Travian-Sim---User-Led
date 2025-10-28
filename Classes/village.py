import Classes.base_squares as base_squares
import Base_Data.Building_Data as b_data
import Base_Data.Fields_Data as f_data
import Generic_Functions.generic_functions as gen_func
import random

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
        self.buildings[1] = ['warehouse', 0, True]
        self.buildings[2] = ['granary', 0, True]

        #default instantiation values
        self.storage_cap = [800, 800, 800, 800]
        self.stored = [800,800,800,800]
        self.currently_upgrading = []
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
        crop_usage = 0
        for key3 in self.fields:
            if 'Wood' in key3:
                wood_yield += self.fields[key3].field_yield
                crop_usage += self.fields[key3].pop
            if 'Clay' in key3:
                clay_yield += self.fields[key3].field_yield
                crop_usage += self.fields[key3].pop
            if 'Iron' in key3:
                iron_yield += self.fields[key3].field_yield
                crop_usage += self.fields[key3].pop
            if 'Crop' in key3:
                crop_yield += self.fields[key3].field_yield
                crop_usage += self.fields[key3].pop
        
        #the below is new - removal of the /3600 stage in the above loop does save us about 4 calls per
        #function call, but its still inefficient.
        #issue - this should really be added later, and just happen at base value level, but cba atm
        wood_yield = wood_yield/3600
        clay_yield = clay_yield/3600
        iron_yield = iron_yield/3600
        crop_yield = (crop_yield-crop_usage)/3600

        yields = [wood_yield, clay_yield, iron_yield, crop_yield]
        return yields
    
    
    def possible_buildings(self):
        #modified to dictionary variant to store both in one item
        possible_buildings = {'buildings' : [], 'fields' : []}
        for key in self.buildings:
            holdval = self.buildings[key]
            #if buildings exist that can be built
            if len(holdval) > 1:
                holdval_level = holdval[1]
                #if upgradeable
                if holdval[2] == True:
                    keyval = holdval[0]
                    upgrade_cost = b_data.building_dict[keyval][holdval_level][0]
                    #default to assuming enough res, then make false if not true
                    enough_res = True
                    for i in range(4):
                        if upgrade_cost[i] > self.stored[i]:
                            enough_res = False
                    if enough_res:
                        #builings go in appropriate dict entry
                        #passed as a two part list, to provide the key and the name
                        final_value = [key, holdval[0]]
                        dictval = possible_buildings['buildings']
                        dictval.append(final_value)
        for key in self.fields:
            holdval = self.fields[key]
            holdval_level = holdval.level
            key2 = key[:4]
            upgrade_cost = f_data.field_dict[key2][holdval_level][0]
            if len(upgrade_cost) > 1:
                enough_res = True
                for i in range(4):
                    if upgrade_cost[i] > self.stored[i]:
                        enough_res = False
                if enough_res:
                # [ISS-005][ISS-006] legacy structure still relies on cost list sentinel
                # and returns a differently shaped payload; refactor when tidying upgrade flow.
                    #fields go in appropriate dict entry
                    final_value = [key]
                    dictval = possible_buildings['fields']
                    dictval.append(final_value)
        return possible_buildings   
    
    def upgrade_building(self, upgrade_target):
        #built and designed for the 2 key building logic in possible_buildings
        building_dict_key = upgrade_target[0]
        building_data_key = upgrade_target[1]
        relevant_target = self.buildings[building_dict_key]
        current_level = relevant_target[1]
        upgradeable_check = relevant_target[2]
        #this is fine for now, and should never trigger. But it is crude.
        #Issue - this is a case where we need better logging functionality.
        if upgradeable_check != True:
            raise ValueError ("You appear to have attempted to upgrade a building that cannot be upgraded :(")
        upgrade_cost = b_data.building_dict[building_data_key][current_level][0]

        #get upgrade time for the building
        upgrade_time = b_data.building_dict[building_data_key][current_level][3]
        # [ISS-007] issue - this does not factor in main building time, needs to be built in in the future
        true_upgrade_time = gen_func.sec_val(upgrade_time)

        #subtract the cost of the ugprade from the village
        hold_vals = self.stored
        for i in range(len(hold_vals)):
            hold_vals[i] -= upgrade_cost[i]
        self.stored = hold_vals
        
        #removed a section on upgrading the level of items already here, and shifted it to
        #post build completion in new function

        sleep_duration = true_upgrade_time
        return sleep_duration
    
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
        #issue - this will not work as planned currently, as it does not factor in
        #the main building imapct on duration
        true_upgrade_time = gen_func.sec_val(upgrade_time)

        #remove cost of everything used for upgrades
        hold_vals = self.stored
        for i in range(len(hold_vals)):
            hold_vals[i] -= upgrade_cost[i]
        self.stored = hold_vals
        self.currently_upgrading.append([upgrade_target])

        sleep_duration = true_upgrade_time
        return sleep_duration


    def building_upgraded(self, upgrade_target):

        #same start code as above
        #built and designed for the 2 key building logic in possible_buildings
        building_dict_key = upgrade_target[0]
        building_data_key = upgrade_target[1]
        relevant_target = self.buildings[building_dict_key]
        current_level = relevant_target[1]
        upgradeable_check = relevant_target[2]

        #this is imperfect, but should work fine - you can't ugprade if its not upgradeable
        #so not risk of overflow error
        #however, this is still an extant issue, as it uses the false flag.
        level_plusone = current_level + 1
        still_upgradeable = b_data.building_dict[building_data_key][level_plusone][0]
        if still_upgradeable[0] == False:
            upgrade_possible = False
        else:
            upgrade_possible = True

        #applying the new values derived above for the upgraded building
        old_vals = self.buildings[building_dict_key]
        old_vals[2] = upgrade_possible
        old_vals[1] = level_plusone
        #potentially not needed, superflous step
        self.buildings[building_dict_key] = old_vals
        old_entry = b_data.building_dict[building_data_key][current_level]
        new_entry = b_data.building_dict[building_data_key][level_plusone]
        pop_delta = new_entry[2] - old_entry[2]
        self.population += pop_delta
        self.culture_points_rate += new_entry[1] - old_entry[1]
        #buildings do not directly add yield in the current dataset, so only the population delta applies
        self.total_yield -= pop_delta

        #null list to signify nothing upgrading.
        # [ISS-008] ISSUE : THIS WILL NEED TO BE CHANGED TO BE A SIMPLE REMOVAL OF THE 0TH INDEX
        #to allow for the roman race to be implemented
        self.currently_upgrading = []

        #nothing returned, merely modifies values in place
    
    def field_upgraded(self, upgrade_target):

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
        pop_delta = new_entry[2] - old_entry[2]
        yield_delta = new_entry[4] - old_entry[4]
        self.population += pop_delta
        self.culture_points_rate += new_entry[1] - old_entry[1]
        self.total_yield += yield_delta - pop_delta

        #null list to signify nothing upgrading.
        # [ISS-008] ISSUE : THIS WILL NEED TO BE CHANGED TO BE A SIMPLE REMOVAL OF THE 0TH INDEX
        #to allow for the roman race to be implemented
        self.currently_upgrading = []

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
