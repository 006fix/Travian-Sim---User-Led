import Classes.player as player


def populate_players(num_players):
    player_dict = {}
    for i in range(num_players):
        name = f'Player{i}'
        #key for below = name, quadrant, race
        hold_player = player.Player(name, None, None)
        player_dict[name] = hold_player
    return player_dict