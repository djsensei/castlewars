"""
file where players (aka move-generating algorithms) live

each must take a board and player id as input and return a valid move
"""
from random import choice
from castlewars import Piece


def purely_random(board, pid):
    options = [c for c, t in nameboard.castles[pid].arsenal.iteritems() if t == 0]
    return Piece(choice(options)), choice(range(board.n_lanes))


def jam_random_pieces(board, pid):
    options = [c for c, t in nameboard.castles[pid].arsenal.iteritems() if t == 0]
    return Piece(choice(options)), 0
