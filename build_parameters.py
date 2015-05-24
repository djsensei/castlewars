"""
[
initial: concise identifier for history
speed: squares forward per turn
attack: attack power, in HP
smash: castle attack power, in HP
armor: defensive shield, in HP
hp: health points
attack_range: attack range, in spaces
smash_range: castle attack range, in space
cooldown: number of turns to regenerate spawnability
]
"""
import json

CHAR_ATTRS = ("name",
              "char",
              "speed",
              "attack",
              "smash",
              "armor",
              "hp",
              "attack_range",
              "smash_range",
              "cooldown")

CHARACTERS = [
("pawn", "P",        1, 1, 1, 0, 1, 0, 1, 1),
("archer", "A",      1, 3, 1, 0, 2, 2, 1, 4),
("brute", "B",       1, 2, 2, 2, 3, 0, 1, 4),
("spiked wall", "S", 0, 2, 0, 4, 4, 1, 0, 6),
("horseman", "H",    2, 2, 2, 2, 3, 1, 1, 6),
("catapult", "C",    1, 1, 4, 1, 2, 2, 3, 8)
]

if __name__=='__main__':
    #characters
    char_dict = {}
    for char_tup in CHARACTERS:
        d = {a: char_tup[i] for i, a in enumerate(CHAR_ATTRS)}
        char_dict[d["name"]] = d

    parameters = {"characters": char_dict}

    with open('data/parameters.json', 'w') as wf:
        json.dump(parameters, wf)
