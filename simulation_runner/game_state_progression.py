

#master counter, represents seconds since simulation instantiation
game_counter = 0
#number of times the global controller triggered
turn_counter = 0

#duration since last active review of game counter
time_elapsed = 0

#the duration that will elapse before the next update
time_will_elapse = 0

#this is a global version of when we were last awake
global_last_active = 0

def set_time_elapsed():
    global time_elapsed
    global time_will_elapse
    global global_last_active
    #issue - both of these use singular assignments - will this create issues as i repeatedly modify them
    #in place - should i use == assignment, or copy?
    time_elapsed = time_will_elapse
    global_last_active = game_counter
    #issue - the below probably works, but its a terrible way to design and implement this
    time_will_elapse = "I'm a string because I should never remain one"

def check_passive(map_dict):

    #blank list to populate with upcoming actions
    next_action_list = []
    for key in map_dict:
        holdval = map_dict[key]
        if holdval.type_square in ('habitable', 'oasis'):
            holder = holdval.next_update()
            #issue - does this actually work? I thought i used false flags for no next updates?
            if holder != True:
                next_action_list.append(holder)
    return next_action_list

def check_players(player_dict):

    #blank list to populate with upcoming actions
    next_action_list = []

    #issue - do i really need the below global flags? could i not just pick them up and pass them in?
    #or just modify the lower level functions to use them? seems inefficient 
    global game_counter
    global global_last_active

    for key in player_dict:
        active_player = player_dict[key]
        wait_time = active_player.will_i_act(game_counter, global_last_active)
        next_action_list.append(wait_time)

    return next_action_list

def simulate_time(map_dict, player_dict):

    #issue - as before do i really need to keep flagging these things as global?
    global game_counter
    global time_will_elapse
    global turn_counter

    set_time_elapsed()
    game_counter = game_counter + time_elapsed
    #issue - the below works fine, but i also want something that wakes everyone up at a set duration
    #say every 5 minutes - recalculates all and takes game state snapshot
    #but this can't work with the way the logic is currently encoded sadly
    passive_actions = check_passive(map_dict)
    player_actions = check_players(player_dict)
    all_actions = passive_actions + player_actions

    if len(all_actions) > 0:
        min_elapsed = min(all_actions)
    else:
        #issue - what exactly is this min elapsed doing? Advancing time by only a single second? Why would it ever trigger?
        min_elapsed = 1
    
    time_will_elapse = min_elapsed
    #iterate through as turns, but seems kind of clunky and odd
    #issue - how could i modify this logic to be more useful? Player level actions taken?
    turn_counter += 1







