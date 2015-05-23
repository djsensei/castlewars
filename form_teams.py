"""
[speed, attack, armor, health]
"""
import json

teams = {
    "default": {
        "pawn": [1, 1, 0, 1]
    }
}

if __name__=='__main__':
    with open('data/teams.json', 'w') as wf:
        json.dump(teams, wf)
