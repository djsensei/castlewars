"""
Castle Wars (prototype name :p) is a MOBA-like game designed for play between
    two algorithms. Each player has a castle.
"""

DEFAULT_MATCH_LENGTH = 100
DEFAULT_NUM_LANES = 3
DEFAULT_NUM_SPACES = 5
DEFAULT_TEAM = "default"
TEAMS_FILE = "data/teams.json"
with open(TEAMS_FILE) as rf:
    ALL_TEAMS = json.load(rf)


def load_team(team_name):
    team = ALL_TEAMS[team_name]
    teamdict = {}
    for name, piece in team.iteritems():
        teamdict[name] = Piece(piece)
    return teamdict


class Piece:
    def __init__(self, piecedict):
        self.speed = piecedict['speed']
        self.attack = piecedict['attack']
        self.armor = piecedict['armor']
        self.health = piecedict['health']


class Player:
    def __init__(self, team=DEFAULT_TEAM)


class Game:
    def __init__(self, match):
        self.match = match
        self.winner = None

    def play(self):
        pass


class Match:
    def __init__(self, player1, player2,
                 match_length=DEFAULT_MATCH_LENGTH,
                 n_lanes=DEFAULT_NUM_LANES,
                 n_spaces=DEFAULT_NUM_SPACES):
        self.p1 = player1
        self.p2 = player2
        self.match_length = match_length
        self.n_lanes = n_lanes
        self.n_spaces = n_spaces

    def play(self):
        outcomes = []
        for i in range(self.match_length):
            game = Game(self)
            game.play()
            outcomes.append(game.winner)
