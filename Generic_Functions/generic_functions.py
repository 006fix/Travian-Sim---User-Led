
#upgrade time given as list [x,y,z] where x=hours, y=minutes, z=seconds
def sec_val(mod_list):
    seconds = mod_list[2]
    minutes = mod_list[1] * 60
    hours = mod_list[0] * 60 * 60

    total_seconds = int(seconds +minutes +hours)

    return total_seconds