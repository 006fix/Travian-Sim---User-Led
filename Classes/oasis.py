import Classes.base_squares as loc_sq
import random

class Oasis(loc_sq.Square):
    def __init__(self, location):
        super().__init__(location)
        self.type_square = 'oasis'
        self.interactable = False
        self.resources = []
        # type one addition
        randval = random.randint(0, 100)
        if randval < 25:
            self.resources.append('wood')
        elif randval < 50:
            self.resources.append('clay')
        elif randval < 75:
            self.resources.append('iron')
        elif randval <= 100:
            self.resources.append('crop')
        #type two addition for dual type oases
        randval = random.randint(0 ,100)
        if randval > 80:
            self.resources.append('crop')
        # now define the storage
        self.storage = []
        #ammended below code heavily - unsure why it used to input dual list types.
        #Now simply creates 3600 (if res present) or 1800 (if res not)
        if 'wood' in self.resources:
            self.storage.append(3600)
        else:
            self.storage.append(1800)
        if 'clay' in self.resources:
            self.storage.append(3600)
        else:
            self.storage.append(1800)
        if 'iron' in self.resources:
            self.storage.append(3600)
        else:
            self.storage.append(1800)
        if 'crop' in self.resources:
            self.storage.append(3600)
        else:
            self.storage.append(1800)

        #below is a holder that makes them non interactable for now
        self.next_action = False
    
    def next_update(self):
        # [ISS-003] resolved: oases remain non-interactable until active behaviour is implemented.
        return None
