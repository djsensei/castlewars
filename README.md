# Castlewars
Castlewars is an algorithm vs. algorithm MOBA-like computer battle in which the "players" are actually just two pre-programmed strategy functions.

## The Players
The sole purpose of each "player" is to make a single decision about which character to spawn and which lane to place them in. To inform this decision, each player has access to the current state of the board as well as the entire history of the current match.

### Valid Player
A valid player is any function that takes as input a `Match` object and a binary `playerid` and yields as output a valid `(Piece, lane)` tuple representing their current move.

## The Game
The objective of the game is to destroy your opponent's castle by inflicting enough cumulative damage upon it. Whichever player smashes up their opponents castle first wins! If both players simultaneously smash each other's castles, it is a tie. Everyone hates ties.

### Board
The game board consists of an array of lanes, each with the same number of cells. Each player has a castle at their end of the lanes. Characters are placed in a lane when they spawn, and must remain in their lane permanently. After the resolution of a turn, no cell may contain more than one character.

### Turns
Each turn, each player chooses a character to release and a lane to send it out in. All characters on the board then simultaneously move and attack, and the turn ends when all motion and combat is resolved.

#### Stages of a Turn

1. *Move* - Each character on the board moves forward some number of squares according to its speed. Two characters from the same team cannot occupy the same space, so if a move would cause one character to join his teammate, it instead pushes that teammate forward.
2. *Battle* - All characters who have an enemy within their range simultaneously deal their attack damage to the nearest enemy. This repeats until no surviving character has an enemy in range.
3. *Smash* - If a character survives battle _and_ is within smash range of the enemy castle, it will deal its smash damage to the enemy castle. Huzzah!

### Characters
Each character has the following integer-valued attributes:

*  `speed`: number of spaces to move forward per turn
*  `attack`: attack power
*  `smash`: castle attack power
*  `armor`: defensive shield (regenerates after each turn)
*  `hp`: health points (when they reach 0, the character disappears)
*  `attack_range`: attack range, in spaces
*  `smash_range`: castle attack range, in spaces
*  `cooldown`: number of turns before the player can spawn this character again

Current Characters include:

*  Pawn (weak but always available)
*  Archer (weak, but with ranged attack)
*  Brute (slow but strong and armored)
*  Horseman (fast and armored)
*  Spiked Wall (great defense, but does not move on its own)
*  Catapult (designed for smashing castles)
