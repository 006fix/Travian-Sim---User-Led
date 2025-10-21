import Classes.base_squares as base_squares
import Classes.habitable as habitable
import Classes.oasis as oasis

def map_creation(map_radius):
    map_dict = {}
    for x in range((map_radius*-1), map_radius+1):
        for y in range((map_radius*-1), map_radius+1):
            #ammended locval to ensure readability in all scenarios
            #i.e 201, 1, and 20,11 would look identical without the slash
            # [ISS-001] note: stringified coordinates may interfere with downstream consumers expecting numeric pairs.
            locval = [x,"/",y]
            dict_key = str(locval)
            map_dict[dict_key] = base_squares.Square(locval)
    return map_dict

def modify_base_map(map_dict):
    for key in map_dict:
        value = map_dict[key]
        if value.type_square == 'wilderness':
            #left in in case we need to modify this later
            pass
        if value.type_square == 'habitable':
            new_obj = habitable.Habitable(key)
            map_dict[key] = new_obj
        if value.type_square == 'oasis':
            new_obj = oasis.Oasis(key)
            map_dict[key] = new_obj
    return map_dict


