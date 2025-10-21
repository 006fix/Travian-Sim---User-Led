import Generic_Functions.generic_functions as generic_func
import Base_Data.Fields_Data as f_data

class Field():
    def __init__(self, type_field, upgradeable=True,level=0):
        #high level logic
        self.type_field = type_field
        self.level=level
        #low level logic
        self.upgrade_cost = f_data.field_dict[self.type_field][self.level][0]
        #the below used to be int forced but I don't know why, lets see if it breaks without it.
        self.field_yield = (f_data.field_dict[self.type_field][self.level][4])
        self.cp = (f_data.field_dict[self.type_field][self.level][1])
        self.pop = (f_data.field_dict[self.type_field][self.level][2])
        self.upgrade_time = (generic_func.sec_val(f_data.field_dict[self.type_field][self.level][3]))
        self.upgradeable = upgradeable