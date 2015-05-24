"""
file where players (aka move-generating algorithms) live

each must take a match and player id as input and return a valid move (or None)
"""
from random import choice
import castlewars as cw

def safechoice(l):
    if not l:
        return None
    return choice(list(l))


def purely_random(match, pid):
    options = match.current_game.board.castles[pid].options()
    char = safechoice(options)
    if char is not None:
        piece = cw.Piece(char, pid)
        lane = choice(range(match.current_game.board.n_lanes))
        return piece, lane
    else:
        return None


def jam_random_pieces(match, pid):
    options = match.current_game.board.castles[pid].options()
    char = safechoice(options)
    if char is not None:
        piece = cw.Piece(char, pid)
        lane = 0
        return piece, lane
    else:
        return None


def human(match, pid):
    # human player - needs a visible board output and a way to give input
    pass


def pawn_train(match, pid):
    piece = cw.Piece("pawn", pid)
    lane = choice(range(match.current_game.board.n_lanes))
    return piece, lane
