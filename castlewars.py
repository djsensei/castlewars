"""
Castle Wars (prototype name :p) is a MOBA-like game designed for play between
    two algorithms. Each player has a castle.
"""
import json
import players


DEFAULT_WIN_CONDITION = "destroy_castle"  # maximum_damage
DEFAULT_MATCH_LENGTH = 100
DEFAULT_GAME_LENGTH = 100
DEFAULT_NUM_LANES = 3
DEFAULT_NUM_CELLS = 5
DEFAULT_CASTLE_HP = 30
BT = (0, 1)

# Load parameters
PARAMS_FILE = "data/parameters.json"
with open(PARAMS_FILE) as rf:
    params = json.load(rf)
    CHARACTERS = params['characters']


class Cell:
    """
    A square of the game board. May or may not contain a Piece from
        either team at any time. If it contains pieces from both teams:
        BATTLE!
    """
    def __init__(self):
        self.pieces = [None, None]

    def get_teams(self):
        return [p is not None for p in self.pieces]

    def battle(self):
        # both teams are present!
        return all(self.get_teams())


class Lane:
    """
    A lane of the game board. Made of Cells.
    """
    def __init__(self, id, n_cells=DEFAULT_NUM_CELLS):
        self.lid = lid  # lane id
        self.n = n_cells
        self.cells = [Cell() for _ in range(n_cells)]

    def is_empty(self):
        return all([c.piece is None for c in self.cells])

    def has_attacker(self, target_castle):
        # is this castle under attack?
        return self.cells[target_castle].get_team()[1 - target_castle]

    def resolve(self, newpieces=(None, None)):  # TODO
        pass
        # bash other castle if you can
        # move pieces forward from front to back
        #    if you hit a teammate, stop
        # if opponent in range, fire until dead and/or he is
        #    fire at nearest opponent (starting with same cell)
        # handle cooldowns and armor regen
        # board.castles[self.pid].arsenal[piece.name] += piece.cooldown


class Castle:
    def __init__(self, hp=DEFAULT_CASTLE_HP):
        self.hp = hp
        self.arsenal = {c: 0 for c in CHARACTERS}  # {character: cooldown turns remaining}

    def spawn(self, char):
        # release a character and update the cooldowns
        assert(self.arsenal[char] == 0)
        self.arsenal[char] += CHARACTERS[char]['cooldown']
        for c, cd in self.arsenal.iteritems():
            if cd > 0:
                cd -= 1

    def take_damage(self, damage):
        self.hp -= damage

    def dead(self):
        return self.hp <= 0


class GameBoard:
    def __init__(self,
                 n_lanes=DEFAULT_NUM_LANES,
                 n_cells=DEFAULT_NUM_CELLS):
        self.n_lanes = n_lanes
        self.board = [Lane(i, n_cells) for i in n_lanes]
        self.castles = [Castle(), Castle()]

    def resolve(self, moves):
        # here are two (Piece, lane) moves, resolve them
        for i in BT:
            self.castles[i].spawn(moves[i][0].name)
        for lane in self.board:
            lanemoves = [None, None]
            for p in BT:
                if moves[p][1] == lane.lid:
                    lanemoves[p] = moves[p][0]
            lane.resolve(lanemoves)


class Piece:
    def __init__(self, name, team):
        self.name = name
        self.char = CHARACTERS[name]['char']
        self.speed = CHARACTERS[name]['speed']
        self.attack = CHARACTERS[name]['attack']
        self.armor = CHARACTERS[name]['armor']
        self.hp = CHARACTERS[name]['hp']
        self.range = CHARACTERS[name]['range']
        self.cooldown = CHARACTERS[name]['cooldown']
        self.team = team

    def take_damage(self, damage):
        if self.armor == 0:
            self.hp -= damage
        elif self.armor < damage:
            self.hp -= damage - self.armor
            self.armor = 0
        else:
            self.armor -= damage

    def dead(self):
        return self.hp <= 0

    def restore_armor(self):
        self.armor = CHARACTERS[self.name]['armor']


class Player:
    def __init__(self, pid, strategy):
        self.strategy = strategy
        self.pid = pid  # 0 or 1

    def turn(self, match):
        # make a decision: (piece, lane)
        return self.strategy(match, self.pid)


class Game:
    def __init__(self, match):
        self.match = match
        self.winner = None
        self.history = ""  # 'p0 piece' + 'p0 lane' + 'p1 piece' + 'p1 lane' + _
        self.turn = 0
        self.board = GameBoard(self.match.n_lanes, self.match.n_cells)

    def play(self):
        # play a game to completion
        while True:
            self.play_turn()
            go = self.is_game_over()
            if go is not None:
                self.history += '__' + str(go)
                self.winner = go
                return

    def play_turn(self):
        self.turn += 1
        # select and resolve moves
        moves = [self.match.p[i].turn(self.board) for i in BT]
        self.board.resolve(moves)
        # update history
        movechars = ''.join([moves[i][0].char + str(moves[i][1]) for i in BT])
        self.history += '_' + movechars

    def is_game_over(self):
        # check the winning condition
        if self.match.win_condition == 'destroy_castle':
            cd = [self.board.castles[c].dead() for c in BT]
            if cd[0]:
                if cd[1]:
                    return "tie"  # TODO - tiebreaker?
                else:
                    return 1  # 1 destroyed 0
            elif cd[1]:
                return 0  # 0 destroyed 1
            else:
                return None
        elif self.match.win_condition == 'maximum_damage':
            if self.turn >= self.match.game_len:
                cscores = [self.board.castles[c].hp for c in BT]
                if cscores[0] == cscores[1]:
                    return "tie"
                elif cscores[0] > cscores[1]:
                    return 0
                else:
                    return 1
            else:
                return None
        else:
            # future winning conditions!
            return "BAD WINNING CONDITION"


class Match:
    def __init__(self,
                 players,
                 win_condition=DEFAULT_WIN_CONDITION,
                 match_length=DEFAULT_MATCH_LENGTH,
                 game_length=DEFAULT_GAME_LENGTH,
                 n_lanes=DEFAULT_NUM_LANES,
                 n_cells=DEFAULT_NUM_CELLS,
                 init_castle_hp=DEFAULT_CASTLE_HP):
        self.p = players  # [p0, p1]
        self.win_condition = win_condition
        self.match_len = match_length
        self.game_len = game_length
        self.n_lanes = n_lanes
        self.n_cells = n_cells
        self.score = [0, 0]  # wins by player 0, player 1 in the match
        self.history = []  # raw history.
        self.init_castle_hp = init_castle_hp
        self.current_game = None

    def write_history(self, filename):
        with open(filename, 'w') as wf:
            for h in self.history:
                wf.write(h + '\n')

    def play(self):
        outcomes = []
        for i in range(self.match_len):
            game = Game(self)
            self.current_game = game
            game.play()
            outcomes.append(game.winner)
            self.history.append(game.history)


if __name__ == '__main__':
    players = [players.purely_random, players.jam_random_pieces]
    match = Match(players)
    match.play()
    match.write_history('history/random_vs_jam.txt')
    print match.score
