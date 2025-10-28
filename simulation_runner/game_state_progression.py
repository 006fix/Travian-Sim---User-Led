

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

from simulation_runner import run_logger

def set_time_elapsed():
    global time_elapsed
    global time_will_elapse
    global global_last_active
    # [ISS-016] these assignments mutate shared globals each tick; refactor into a kernel with immutable snapshots.
    time_elapsed = time_will_elapse
    global_last_active = game_counter
    # [ISS-016] placeholder sentinel; remove once scheduler manages delays explicitly.
    time_will_elapse = "I'm a string because I should never remain one"

def check_passive(map_dict):

    #blank list to populate with upcoming actions
    next_action_list = []
    for key in map_dict:
        holdval = map_dict[key]
        if holdval.type_square in ('habitable', 'oasis'):
            holder = holdval.next_update()
            # [ISS-017] clarify next_update contract (should return numeric or None, not True/False).
            if holder != True:
                next_action_list.append(holder)
    return next_action_list

def check_players(player_dict):

    #blank list to populate with upcoming actions
    next_action_list = []

    # [ISS-018] globals couple scheduler to module state; replace with an injected GameState.
    global game_counter
    global global_last_active

    for key in player_dict:
        active_player = player_dict[key]
        wait_time = active_player.will_i_act(game_counter, global_last_active)
        next_action_list.append(wait_time)

    return next_action_list

def simulate_time(map_dict, player_dict):

    # [ISS-018] globals to be phased out once kernel encapsulation lands.
    global game_counter
    global time_will_elapse
    global turn_counter

    set_time_elapsed()
    game_counter = game_counter + time_elapsed
    # [ISS-020] add heartbeat / logging once scheduler formalised.
    passive_actions = check_passive(map_dict)
    player_actions = check_players(player_dict)
    all_actions = passive_actions + player_actions

    if len(all_actions) > 0:
        min_elapsed = min(all_actions)
    else:
        # [ISS-019] temporal fallback hides stalled sims; replace with heartbeat event or explicit guard.
        min_elapsed = 1

    run_logger.log_tick(
        turn=turn_counter,
        game_time=game_counter,
        elapsed=time_elapsed,
        scheduled_delay=min_elapsed,
        passive_candidates=passive_actions,
        player_candidates=player_actions,
    )

    time_will_elapse = min_elapsed
    # [ISS-020] enrich metrics/logging once kernel endorses tick summaries.
    turn_counter += 1







