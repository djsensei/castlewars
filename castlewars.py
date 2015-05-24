"""
Castle Wars (prototype name :p) is a MOBA-like game designed for play between
    two algorithms. Each player has a castle.
"""
import json
import players


DEFAULT_WIN_CONDITION = "destroy_castle"  # maximum_damage
DEFAULT_MATCH_LENGTH = 1
DEFAULT_GAME_LENGTH = 10
DEFAULT_NUM_LANES = 2
DEFAULT_NUM_CELLS = 5
DEFAULT_CASTLE_HP = 30
BT = (0, 1)  # binary tuple. very useful for iterating over teams!

# Load parameters
PARAMS_FILE = "data/parameters.json"
with open(PARAMS_FILE) as rf:
    params = json.load(rf)
    CHARACTERS = params['characters']


def movestring(move):
    """
    Returns a brief string representing this move, for writing to history
    """
    if move is None:
        return "nm"
    return move[0].char + str(move[1])


class Cell:
    """
    A square of the game board. May or may not contain a Piece from
        either team at any time. If it contains pieces from both teams:
        BATTLE!
    """
    def __init__(self, loc):
        self.loc = loc  # index in the lane
        self.pieces = [None, None]

    def __repr__(self):
        if self.pieces[0] is not None:
            return self.pieces[0].char + '-0'
        if self.pieces[0] is not None:
            return self.pieces[1].char + '-1'
        return ' x '

    def get_teams(self):
        return [p is not None for p in self.pieces]

    def lacks(self, p):
        return self.pieces[p] is None


class Lane:
    """
    A lane of the game board. Made of Cells.
    """
    def __init__(self, lid, n_cells=DEFAULT_NUM_CELLS):
        self.lid = lid  # lane id
        self.n = n_cells
        self.cells = [Cell(i) for i in range(n_cells)]
        self.cells_ftr = (tuple(range(n_cells - 1, -1, -1)), tuple(range(n_cells)))

    def __repr__(self):
        return ' _ '.join([str(c) for c in self.cells])

    def is_empty(self):
        return all([c.piece is None for c in self.cells])

    def has_attacker(self, target_castle):
        # is this castle under attack?
        return self.cells[target_castle].get_team()[1 - target_castle]

    def resolve(self, newpieces=(None, None)):
        """
        Resolves a turn for this lane
        Returns a list of damage to castles
        """
        # move
        self._move_all(newpieces)
        # battle
        self._battle()
        # smash
        return self._smash()

    def _move_all(self, newpieces):
        for p in BT:
            self._move_team(p, newpieces[p])

    def _move_team(self, p, newpiece):
        """
        Move all characters on this team, then return
        """
        # order characters from front to rear
        team = []  # (Piece, cell) tuples
        for c in self.cells_ftr[p]:
            piece = self.cells[c].pieces[p]
            if piece is not None:
                team.append((piece, c))

        # march all characters forward
        for piece, cell in team:
            self._march(piece, cell)

        # add new character to the beginning, if possible
        if self.cells[p * (self.n - 1)].pieces[p] is None:
            self.cells[p * (self.n - 1)].pieces[p] = newpiece

    def _march(self, piece, cell):
        """
        Move this piece forward
        """
        p = piece.team
        dst = self.cells_ftr[p].index(cell) - piece.speed
        dst_cell = self.cells_ftr[p][max((0, dst))]
        while dst_cell > cell:
            dst_piece = self.cells[dst_cell].pieces[p]
            if dst_piece is None:
                # we can move there!
                self._move_piece(p, cell, dst_cell)
                continue
            if dst > 0 and dst_piece.speed == 0:
                # is someone else in the push spot already?
                push_cell = dst_cell - 1
                push_piece = self.cells[push_cell].pieces[p]
                if push_piece is None:
                    # hooray! push push push
                    self._move_piece(p, dst_cell, push_cell)
                    self._move_piece(p, cell, dst_cell)
                    continue
            dst += 1
            dst_cell = self.cells_ftr[p][max((0, dst))]

    def _move_piece(self, p, src, dst):
        """
        Move piece from src cell to dst cell
        """
        assert(self.cells[dst].pieces[p] is None)
        self.cells[dst].pieces[p] = self.cells[src].pieces[p]
        self.cells[src].pieces[p] = None

    def _get_all_targets(self):
        """
        Returns a list of (piece, damage) tuples for all characters who
            will take damage in an attack round
        """
        targets = []
        for cell in self.cells:
            for p in BT:
                piece = cell.pieces[p]
                target = self._get_target(piece, cell.loc)
                if target is not None:
                    targets.append((target, piece.attack))

    def _get_target(self, piece, loc):
        """
        For the given piece and location, return a target piece or None
        """
        if piece is None:
            return None
        # cell_checklist is the ordered list of cells to check for a target
        if piece.team == 0:
            cell_checklist = range(loc, loc + piece.attack_range + 1)
        else:
            cell_checklist = range(loc, loc - piece.attack_range - 1, -1)
        for c in cell_checklist:
            opponent = self.cells[c].pieces[1 - piece.team]
            if opponent is not None:
                return opponent
        return None

    def _battle(self):
        """
        FIGHT TO THE DEATH
        """
        targets = self._get_all_targets()
        while targets is not None:
            for target, damage in targets:
                target.take_damage(damage)
            self._remove_corpses()
            targets = self._get_targets()

    def _remove_corpses(self):
        """
        Remove dead characters from the lane
        TODO - write to history
        """
        for cell in self.cells:
            for p in BT:
                if cell.pieces[p] is not None and cell.pieces[p].hp <= 0:
                    cell.pieces[p] = None

    def _smashable(self):
        """
        Return a list of all pieces who can smash their opponent's castle
        """
        smashpieces = []
        for i, c in enumerate(self.cells):
            c_dist = (self.n - i, i + 1)  # distance to castle for both teams
            for team in BT:
                p = c.pieces[team]
                if p is not None and p.smash_range <= c_dist[team]:
                    smashpieces.append(p)
        return smashpieces

    def _smash(self):
        """
        Returns a list of smash damage to both castles: [d0, d1]
        """
        damage = [0, 0]
        for piece in self._smashable():
            damage[1 - piece.team] += piece.smash
        return damage


class Castle:
    def __init__(self, hp=DEFAULT_CASTLE_HP):
        self.hp = hp
        self.arsenal = {c: 0 for c in CHARACTERS}  # {character: remaining_cooldown}

    def __repr__(self):
        return 'HP: ' + self.hp + '\n' + '\n'.join([c + ': ' + str(v) for c, v in self.arsenal.iteritems()])

    def options(self):
        return tuple(c for c, t in self.arsenal.iteritems() if t == 0)

    def spawn(self, char):
        # release a character
        assert(self.arsenal[char] == 0)
        self.arsenal[char] += CHARACTERS[char]['cooldown']

    def cooldown(self):
        # cooldown all characters
        for c in self.arsenal:
            if self.arsenal[c] > 0:
                self.arsenal[c] -= 1

    def take_damage(self, damage):
        self.hp -= damage

    def dead(self):
        return self.hp <= 0


class Board:
    def __init__(self,
                 n_lanes=DEFAULT_NUM_LANES,
                 n_cells=DEFAULT_NUM_CELLS):
        self.n_lanes = n_lanes
        self.board = [Lane(i, n_cells) for i in range(n_lanes)]
        self.castles = [Castle(), Castle()]

    def __repr__(self):
        castles = 'C0: ' + str(self.castles[0].hp) + ' ' + 'C1: ' + str(self.castles[1].hp)
        rows = [str(l) for l in self.board]
        return '\n'.join([castles] + rows)

    def resolve(self, moves):
        """
        Resolves a turn, given two (Piece, lane) moves
        """
        # resolve cooldowns
        for i in BT:
            if moves[i] is not None:
                self.castles[i].spawn(moves[i][0].name)
            self.castles[i].cooldown()

        # resolve action in each lane
        for lane in self.board:
            lanemoves = [None, None]
            for p in BT:
                if moves[p] is not None and moves[p][1] == lane.lid:
                    lanemoves[p] = moves[p][0]
            damages = lane.resolve(lanemoves)
            for i, d in enumerate(damages):
                self.castles[i].hp -= d

    def better_castle(self):
        """
        Returns the id of the player with the healthiest castle (or "tie")
        """
        cscores = [self.castles[c].hp for c in BT]
        if cscores[0] == cscores[1]:
            return "tie"
        elif cscores[0] > cscores[1]:
            return 0
        else:
            return 1


class Piece:
    def __init__(self, name, team):
        self.name = name
        cd = CHARACTERS[name]
        self.char = cd['char']
        self.speed = cd['speed']
        self.attack = cd['attack']
        self.smash = cd['smash']
        self.armor = cd['armor']
        self.hp = cd['hp']
        self.attack_range = cd['attack_range']
        self.smash_range = cd['smash_range']
        self.cooldown = cd['cooldown']
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
        self.history = [None] * match.game_len  # TODO - use History object
        self.turn = 0
        self.board = Board(self.match.n_lanes, self.match.n_cells)

    def play(self):
        # play a game to completion
        while True:
            go = self.take_turn()
            if go is not None:
                # TODO add winner string
                # self.history += '__' + str(go)
                self.winner = go
                return

    def take_turn(self):
        # select and resolve moves
        moves = [self.match.p[i](self.match, i) for i in BT]
        self.board.resolve(moves)

        # update history
        self.history[self.turn] = ''.join([movestring(m) for m in moves])

        self.turn += 1
        return self.is_game_over()

    def is_game_over(self):
        # check the winning condition
        if self.turn >= self.match.game_len:
            return self.board.better_castle()
        if self.match.win_condition == 'destroy_castle':
            cd = tuple(self.board.castles[c].dead() for c in BT)
            if cd[0]:
                if cd[1]:
                    return "tie"  # TODO - tiebreaker?
                else:
                    return 1  # 1 destroyed 0
            elif cd[1]:
                return 0  # 0 destroyed 1
            else:
                return None
        if self.match.win_condition == 'maximum_damage':
            return self.board.better_castle()
        return None


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


class History:
    def __init__(self):
        pass

    def load_from_file(self, filename):
        """
        Loads history from file to object
        """
        pass

    def write_to_file(self, filename):
        """
        Serializes history object to file
        """
        pass


if __name__ == '__main__':
    players = [players.purely_random, players.jam_random_pieces]
    match = Match(players)
    match.play()
    match.write_history('history/random_vs_jam.txt')
    print match.score
