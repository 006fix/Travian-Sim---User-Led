
class Player:
    def __init__(self, name, quadrant, race, ai_controller,
                 population=0, attack_points=0, defence_points=0, raid_points=0, culture_points=0):
        self.name = name
        self.quadrant = quadrant
        self.race = race
        self.ai_controller = ai_controller
        self.culture_points = culture_points
        self.population = population
        self.attack_points = attack_points
        self.defence_points = defence_points
        self.raid_points = raid_points
        #ammended villages from a global list in input to avoid potential issues
        self.villages = []
        #below used to exist - doesn't make sense, players don't have a location, that should be stored under villages
        #self.location = 'None'
        self.Last_Active = 0
        self.Sleep = False


        self.next_action = False

    def next_update(self):
        # [ISS-004] placeholder scheduling logic; replace when proper event handling is built.
        if self.next_action == False:
            wait_duration = True
        else:
            wait_duration = self.next_action
        return wait_duration
