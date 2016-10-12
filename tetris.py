# Simple tetris program! v0.2
# D. Crandall, Sept 2016

from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
from TetrisGame import *
import time, sys
import copy
debug = 1

# min_height = 8000

def heuristic_height(board):
    height = [0] * 10
    # print "In heuristic"
    # print board
    for r in range(0, len(board)):
        for c in range(0, 10):
            if board[r][c] == 'x' and height[c] == 0:
                height[c] = len(board) - r
    # print height
    agg_ht = 0
    for h in range(0, len(height)):
        agg_ht += height[h]
    return agg_ht

def heuristic_complete(board):
    complete_lines = 0
    for r in range(0, len(board)):
        complete_lines += 1
        for col in range(0, 10):
            if board[r][col] == ' ':
                complete_lines -= 1
                break
    return complete_lines

def heuristic_emptiness(board):
    height = [0] * 10
    empty_blocks = 0
    # print "In heuristic"
    # print board
    for r in range(0, len(board)):
        for c in range(0, 10):
            if board[r][c] == 'x' and height[c] == 0:
                height[c] = len(board) - r
                if c > 0:
                    empty_blocks += abs(height[c] - height[c-1])
    return empty_blocks

def heuristic_holes(board):
    holes = 0
    # print "In heuristic"
    # print board
    for c in range(0, 10):
        filled_cells = 0
        for r in range(0, len(board)):
            if board[r][c] == 'x':
                filled_cells = 1
            else:
                if board[r][c] == ' ' and filled_cells == 1:
                    holes += 1
    return holes

def get_heuristic((board, score)):
    # return heuristic_height(board) + heuristic_emptiness(board) - heuristic_complete(board)
    return (0.25 * heuristic_height(board)) + (0.15 * heuristic_emptiness(board)) + \
           (0.10 * heuristic_holes(board)) + (-0.50 * heuristic_complete(board))

class HumanPlayer:
    def get_moves(self, tetris):
        print "Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\nThen press enter. E.g.: bbbnn\n"
        moves = raw_input()
        return moves

    def control_game(self, tetris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": tetris.left, "n": tetris.rotate, "m": tetris.right, " ": tetris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:
    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. tetris is an object that lets you inspect the board, e.g.:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #


    def get_moves(self, tetris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        # Added for testing
        print tetris.col, tetris.row
        # print tetris.rotate()
        # print tetris.get_piece()
        # print tetris.get_next_piece()
        print tetris.get_board()
        b = copy.deepcopy(tetris)
        board = b.get_board()
        # score = TetrisGame.get_score(b)
        score = 0
        # b.down()
        min_heuristic = 8000
        min_col = 21
        min_row = 21
        min_rot = 0
        print len(b.get_board())
        rotation = 0
        while (rotation < 4):
            for row in range(0, len(b.get_board())):
                for col in range(0, 10):
                    if board[row][col] != 'x':
                        if not (TetrisGame.check_collision((board, score), b.piece, row, col)):
                            new_heuristic = get_heuristic(TetrisGame.place_piece((board, score), b.piece, row, col) )
                            # c_lines = heuristic_complete(TetrisGame.place_piece())
                            # print "After place piece: "
                            # print board
                            if new_heuristic <= min_heuristic:
                                min_heuristic = new_heuristic
                                min_row = row
                                min_col = col
                                min_rot = rotation

            rotation += 1
            b.piece = TetrisGame.rotate_piece(b.piece, 90)
        # print "number of Cols: " + str(len(b.get_board()[1]))
        moves = ''
        if min_rot > 0:
            for i in range(0, min_rot):
                moves += 'n'

        if tetris.col - min_col < 0:
            # print "Reached here"
            for i in range(0, abs(tetris.col - min_col)):
                moves += 'm'
        else:
            for i in range(0, tetris.col - min_col):
                moves += 'b'
        print moves
        print min_heuristic, min_col, min_row, min_rot
        print tetris.row - min_row
        print tetris.col - min_col
        # print abs(tetris.col - min_col)

        return moves

        # return random.choice("mnb") * random.randint(1, 10)
       
    # This is the version that's used by the animated version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "tetris" object to control the movement. In particular:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, tetris):
        # another super simple algorithm: just move piece to the least-full column
        while 1:
            time.sleep(0.1)

            board = tetris.get_board()
            column_heights = [ min([ r for r in range(len(board)-1, 0, -1) if board[r][c] == "x"  ] + [100,] ) for c in range(0, len(board[0]) ) ]
            index = column_heights.index(max(column_heights))

            if(index < tetris.col):
                tetris.left()
            elif(index > tetris.col):
                tetris.right()
            else:
                tetris.down()


###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print "unknown player!"

    if interface_opt == "simple":
        tetris = SimpleTetris()
    elif interface_opt == "animated":
        tetris = AnimatedTetris()
    else:
        print "unknown interface!"

    tetris.start_game(player)

except EndOfGame as s:
    print "\n\n\n", s


# Making some changes again
