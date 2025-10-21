import random

class Location:
    def __init__(self, location):
        self.location = location
        self.interactable = True
        self.owner = None
        self.last_active = 0
        self.sleep = True

class Square(Location):
    def __init__(self, location):
        super().__init__(location)
        randval = random.randint(0,100)
        if randval < 10:
            self.type_square = 'wilderness'
        elif randval < 30:
            self.type_square = 'oasis'
        else:
            self.type_square = 'habitable'
