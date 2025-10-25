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
                    storage = building_data.building_dict['warehouse'][level][4]
                    warehouse_storage += storage
                if 'granary' in holder[0]:
                    level = holder[1]
                    storage = building_data.building_dict['granary'][level][4]
                    granary_storage += storage
            #extra section to stop it setting back to 0 if buildings destroyed
            else:
                no_storage_found = True
        if no_storage_found:
            self.storage_cap = [800,800,800,800]
        else:
            self.storage_cap = [warehouse_storage, warehouse_storage, warehouse_storage, granary_storage]


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
        possible_buildings = [[], []]
        for key in self.buildings:
            # this bottom one is simply for now, since i've put those holders in
            # remove this whole step later
            holdval = self.buildings[key]
            #THIS IS ALSO JUST TO STOP IT BREAKING FROM THE NULL VALUES
            #but maybe keep long term?
            if len(holdval) > 1:
                holdval_level = holdval[1]
                #if upgradeable
                if holdval[2] == True:
                    keyval = holdval[0]
                    #HOW DO I KNOW THE BUILDINGS LEVEL?
                    upgrade_cost = building_data.building_dict[keyval][holdval_level][0]
                    #BOTH ARE REQUIRED, BECAUSE IF COND1-4 ARE TRUE, BUT COND5-8 AREN'T, IT'S A FUTURE POSSIBLE
                    #WORK IT OUT LATER
                    #print(f"My upgrade cost is {upgrade_cost}")
                    #print(f"My storage cap is {self.storage_cap}")
                    cond1 = upgrade_cost[0] < self.storage_cap[0]
                    cond2 = upgrade_cost[1] < self.storage_cap[1]
                    cond3 = upgrade_cost[2] < self.storage_cap[2]
                    cond4 = upgrade_cost[3] < self.storage_cap[3]
                    cond5 = upgrade_cost[0] <= self.stored[0]
                    cond6 = upgrade_cost[1] <= self.stored[1]
                    cond7 = upgrade_cost[2] <= self.stored[2]
                    cond8 = upgrade_cost[3] <= self.stored[3]
                    if cond1 and cond2 and cond3 and cond4 and cond5 and cond6 and cond7 and cond8:
                        #builings go in list 1
                        #passed as a two part list, to provide the key and the name
                        final_value = [key, holdval[0]]
                        possible_buildings[0].append(final_value)
        for key in self.fields:
            holdval = self.fields[key]
            holdval_level = holdval.level
            key2 = key[:4]
            upgrade_cost = fields_data.field_dict[key2][holdval_level][0]
            cond1 = upgrade_cost[0] < self.storage_cap[0]
            cond2 = upgrade_cost[1] < self.storage_cap[1]
            cond3 = upgrade_cost[2] < self.storage_cap[2]
            cond4 = upgrade_cost[3] < self.storage_cap[3]
            cond5 = upgrade_cost[0] <= self.stored[0]
            cond6 = upgrade_cost[1] <= self.stored[1]
            cond7 = upgrade_cost[2] <= self.stored[2]
            cond8 = upgrade_cost[3] <= self.stored[3]
            #new condition added here, since the upgradeability of the fields is stored seperately
            if len(upgrade_cost) > 1 and cond1 and cond2 and cond3 and cond4 and cond5 and cond6 and cond7 and cond8:
                #fields go in list two
                possible_buildings[1].append(key)
        return possible_buildings   

