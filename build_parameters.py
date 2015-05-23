"""
[
initial: concise identifier for history
speed: squares forward per turn
attack: attack power, in HP
armor: defensive shield, in HP
hp: health points
range: attack range, in spaces
respawn: number of turns to regenerate spawnability
]
"""
import json

parameters = {
    "characters": {
        "pawn":        ["P", 1, 1, 1, 1, 0, 1],
        "archer":      ["A", 1, 3, 0, 1, 2, 4],
        "brute":       ["B", 1, 2, 2, 3, 0, 4],
        "spiked wall": ["S", 0, 2, 4, 4, 1, 6],
        "horseman":    ["H", 2, 2, 2, 3, 1, 6]
    }
}

if __name__=='__main__':
    with open('data/parameters.json', 'w') as wf:
        json.dump(parameters, wf)
