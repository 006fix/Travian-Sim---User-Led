
###############
#####WOOD######
###############

#structure of each entry for each level:
#resource cost - wood/clay/iron/crop
#cp
#pop - THIS IS THE SAME AS CROP USAGE
#time to build
#yield
#WOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOOD
wood_dict = {0: [[40, 100, 50, 60], 0, 0, [0, 4, 20], 3], 1: [[65, 165, 85, 100], 1, 2, [0, 10, 20], 7],
                  2:[[110, 280, 140, 165], 1, 3, [0, 19, 50], 13], 3: [[185, 465, 235, 280], 2, 4, [0, 35, 0], 21],
                  4: [[310, 780, 390, 465], 2, 5, [0, 59, 20], 31], 5: [[520, 1300, 650, 780], 2, 6, [1, 38, 10], 46],
                  6: [[870, 2170, 1085, 1300], 3, 8, [2, 40, 20], 70], 7: [[1450, 3625, 1810, 2175], 4, 10, [4, 19, 50], 98],
                  8: [[2420, 6050, 3025, 3630], 4, 12, [6, 59, 10], 140], 9: [[4040, 10105, 5050, 6060], 5, 14, [11, 14, 0], 203],
                  10: [[6750, 16870, 8435, 10125], 6, 16, [18, 1, 40], 280], 11: [[11270, 28175, 14090, 16905], 7, 18, [28, 54, 10], 392],
                  12: [[18820, 47055, 23525, 28230], 9, 20, [46, 18, 0], 525], 13: [[31430, 78580, 39290, 47150], 11, 22, [74, 8, 0], 693],
                  14: [[52490, 131230, 65615, 78740], 13, 24, [118, 40, 10], 889], 15: [[87660, 219155, 109575, 131490], 15, 26, [189, 55, 30], 1120],
                  16: [[146395, 365985, 182995, 219590], 18, 29, [303, 56, 10], 1400], 17: [[False], 22, 32, [False, False, False], 1820]}
#WOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOODWOOD


###############
#####CLAY######
###############

#structure of each entry for each level:
#resource cost - wood/clay/iron/crop
#cp
#pop - THIS IS THE SAME AS CROP USAGE
#time to build
#yield
#CLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAY
clay_dict = {0: [[80, 40, 80, 50], 0, 0, [0, 3, 40], 3], 1: [[135, 65, 135, 85], 1, 2, [0, 9, 10], 7],
                  2:[[225, 110, 225, 140], 1, 3, [0, 18, 0], 13], 3: [[375, 185, 375, 235], 2, 4, [0, 32, 10], 21],
                  4: [[620, 310, 620, 390], 2, 5, [0, 54, 50], 31], 5: [[1040, 520, 1040, 650], 2, 6, [1, 31, 10], 46],
                  6: [[1735, 870, 1735, 1085], 3, 8, [2, 29, 10], 70], 7: [[2900, 1450, 2900, 1810], 4, 10, [4, 2, 0], 98],
                  8: [[4840, 2420, 4840, 3025], 4, 12, [6, 30, 30], 140], 9: [[8080, 4040, 8080, 5050], 5, 14, [10, 28, 10], 203],
                  10: [[13500, 6750, 13500, 8435], 6, 16, [16, 48, 30], 280], 11: [[22540, 11270, 22540, 14090], 7, 18, [26, 56, 50], 392],
                  12: [[37645, 18820, 37645, 23525], 9, 20, [43, 10, 20], 525], 13: [[62865, 31430, 62865, 39290], 11, 22, [69, 7, 50], 693],
                  14: [[104985, 52490, 104985, 65615], 13, 24, [110, 39, 50], 889], 15: [[175320, 87660, 175320, 109575], 15, 26, [177, 7, 0], 1120],
                  16: [[292790, 146395, 292790, 182995], 18, 29, [283, 26, 30], 1400], 17: [[False], 22, 32, [False, False, False], 1820]}
#CLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAYCLAY


###############
#####IRON######
###############

#structure of each entry for each level:
#resource cost - wood/clay/iron/crop
#cp
#pop - THIS IS THE SAME AS CROP USAGE
#time to build
#yield
#IRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRON
iron_dict = {0: [[100, 80, 30, 60], 0, 0, [0, 7, 30], 3], 1: [[165, 135, 50, 100], 1, 3, [0, 15, 20], 7],
                  2:[[280, 225, 85, 165], 1, 5, [0, 27, 50], 13], 3: [[465, 375, 140, 280], 2, 7, [0, 48, 0], 21],
                  4: [[780, 620, 235, 465], 2, 9, [1, 20, 0], 31], 5: [[1300, 1040, 390, 780], 2, 11, [2, 11, 20], 46],
                  6: [[2170, 1735, 650, 1300], 3, 13, [3, 33, 30], 70], 7: [[3625, 2900, 1085, 2175], 4, 15, [5, 44, 50], 98],
                  8: [[6050, 4840, 1815, 3630], 4, 17, [9, 15, 10], 140], 9: [[10105, 8080, 3030, 6060], 5, 19, [14, 51, 40], 203],
                  10: [[16870, 13500, 5060, 10125], 6, 21, [23, 50, 0], 280], 11: [[28175, 22540, 8455, 16905], 7, 24, [38, 11, 10], 392],
                  12: [[47055, 37645, 14115, 28230], 9, 27, [61, 9, 20], 525], 13: [[78580, 62865, 23575, 47150], 11, 30, [97, 54, 10], 693],
                  14: [[131230, 104985, 39370, 78740], 13, 33, [156, 42, 0], 889], 15: [[219155, 175320, 65745, 131490], 15, 36, [250, 46, 30], 1120],
                  16: [[365985, 292790, 109795, 219590], 18, 39, [401, 17, 40], 1400], 17: [[False], 22, 42, [False, False, False], 1820]}
#IRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRONIRON

###############
#####CROP######
###############

#structure of each entry for each level:
#resource cost - wood/clay/iron/crop
#cp
#pop - THIS IS THE SAME AS CROP USAGE
#time to build
#yield
#CROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROP
crop_dict = {0: [[70, 90, 70, 20], 0, 0, [0, 2, 30], 3], 1: [[115, 150, 115, 35], 1, 0, [0, 7, 20], 7],
                  2:[[195, 250, 195, 55], 1, 0, [0, 15, 0], 13], 3: [[325, 420, 325, 95], 2, 0, [0, 27, 30], 21],
                  4: [[545, 700, 545, 155], 2, 0, [0, 47, 10], 31], 5: [[910, 1170, 910, 260], 2, 0, [1, 18, 50], 46],
                  6: [[1520, 1950, 1520, 435], 3, 1, [2, 9, 40], 70], 7: [[2535, 3260, 2535, 725], 4, 2, [3, 30, 40], 98],
                  8: [[4235, 5455, 4235, 1210], 4, 3, [5, 40, 30], 140], 9: [[7070, 9095, 7070, 2020], 5, 4, [9, 8, 0], 203],
                  10: [[11810, 15185, 11810, 3375], 6, 5, [14, 40, 10], 280], 11: [[19725, 25360, 19725, 5635], 7, 6, [23, 31, 40], 392],
                  12: [[32940, 42350, 32940, 9410], 9, 7, [37, 41, 50], 525], 13: [[55005, 70720, 55005, 15715], 11, 8, [60, 22, 20], 693],
                  14: [[91860, 118105, 91860, 26245], 13, 9, [96, 39, 10], 889], 15: [[153405, 197240, 153405, 43830], 15, 10, [154, 41, 50], 1120],
                  16: [[256190, 329395, 256190, 73195], 18, 12, [247, 34, 20], 1400], 17: [[False], 22, 14, [False, False, False], 1820]}
#CROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROPCROPCROPCROPCROPCROPCORPCROPCROP



field_dict = {'Wood': wood_dict, 'Clay': clay_dict, 'Iron': iron_dict, 'Crop': crop_dict}