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
            self.storage_cap = [warehouse_storage, warehouse_storage, warehouse_storage, granary_storage]
            for i in range(len(self.storage_cap)):
                if self.storage_cap[i] < 800:
                    self.storage_cap[i] = 800

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

