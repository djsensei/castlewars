"""
file where players (aka move-generating algorithms) live

each must take a match and player id as input and return a valid move
"""
from random import choice
from castlewars import Piece


def purely_random(match, pid):
    options = [c for c, t in match.current_game.board.castles[pid].arsenal.iteritems() if t == 0]
    return Piece(choice(options)), choice(range(board.n_lanes))


def jam_random_pieces(match, pid):
    options = [c for c, t in match.current_game.board.castles[pid].arsenal.iteritems() if t == 0]
    return Piece(choice(options)), 0

def human(match, pid):
    # human player - needs a visible board output and a way to give input
    pass
