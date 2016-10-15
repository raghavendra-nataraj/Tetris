# Simple Tetris implemented with max_heuristic and updated code for emptiness
# Simple tetris program! v0.2
# D. Crandall, Sept 2016

from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
from TetrisGame import *
import time, sys
import copy

debug = 0


# min_height = 8000

def get_height(board):
    height = [0] * 10
    for r in range(0, len(board)):
        for c in range(0, 10):
            if board[r][c] == 'x' and height[c] == 0:
                height[c] = len(board) - r
    # print height
    return height

def heuristic_height(board):
    height = get_height(board)
    # print "In heuristic height"
    # print board
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
    height = get_height(board)
    empty_blocks = 0
    # print "In heuristic emptiness"
    # print board
    for i in range(0, 9):
        empty_blocks += abs(height[i] - height[i + 1])
    # print "Empty Blocks = " + str(empty_blocks)
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
    # print "Board in get heuristics:"
    # print board
    # print "\n" * 3 + ("Score: %d \n" % score) + "|\n".join(board) + "|\n" + "-" * 10
    # Check if the below values should be changed based on the next piece information
    a = -0.5
    b = -0.2
    c = -0.8
    d = 1
    # return (-25 * heuristic_height(board)) + (-20 * heuristic_emptiness(board)) + \
    #        (-20 * heuristic_holes(board)) + (20 * heuristic_complete(board))
    heuristic = (a * heuristic_height(board)) + (b * heuristic_emptiness(board)) + \
           (c * heuristic_holes(board)) + (d * heuristic_complete(board))
    # print "Heuristic for this board: " + str(heuristic)
    return heuristic


def get_best_row(board, score, piece, col):
    row = 0
    while row < 19:
        if not TetrisGame.check_collision((board, score), piece, row+1, col):
            row+=1
            # print "Row before best row calc" + str(row)
            # best_row = row - 1
        else:
            break

    return row

def get_best_move(board, piece):
    # board = b.get_board()
    score = 0
    max_heuristic = -8000
    min_col = 21
    min_row = 21
    min_rot = 0
    if debug == 1:
        print len(board)
    rotation = 0
    # height = get_height(board)
    while rotation < 3:
        for col in range(0, 10):
            # row = (19 - height[col]) - len(piece) + 1
            row = get_best_row(board, score, piece, col)
            if row > 0:
                # print "Best Row for next piece: " + str(row) + " calculated for col:" + str(col)
                new_heuristic = get_heuristic(TetrisGame.place_piece((board, score), piece, row, col))
                # print "After place piece: "
                # print board
                if new_heuristic >= max_heuristic:
                    max_heuristic = new_heuristic
                    min_row = row
                    min_col = col
                    min_rot = rotation

        rotation += 1
        # print "Rotation of next block:" + str(rotation)
        piece = TetrisGame.rotate_piece(piece, 90)
    return max_heuristic, min_col, min_row, min_rot


class HumanPlayer:
    def get_moves(self, tetris):
        print "Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\nThen press enter. E.g.: bbbnn\n"
        moves = raw_input()
        return moves

    def control_game(self, tetris):
        while 1:
            c = get_char_keyboard()
            commands = {"b": tetris.left, "n": tetris.rotate, "m": tetris.right, " ": tetris.down}
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

    # Computer Simple
    def get_moves(self, tetris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        # Added for testing
        # print tetris.col, tetris.row
        # print "Piece:" + str(tetris.piece)
        # print tetris.rotate()
        # print tetris.get_piece()
        # print tetris.get_next_piece()
        # print tetris.get_board()
        b = copy.deepcopy(tetris)
        board = b.get_board()
        # print len(b.get_board())
        score = 0
        max_heuristic = -8000
        min_col = 21
        min_row = 21
        min_rot = 0
        rotation = 0
        next_piece = b.get_next_piece()
        # height = get_height(board)
        while (rotation < 3):
            # Run below for each piece rotation and each possible position of the current piece
            for col in range(0, 10):
                # row = (19 - height[col]) - len(b.piece) + 1
                row = get_best_row(board, score, b.piece, col)
                if row > 0:
                    # print "Best Row for current piece: " + str(row)  + " calculated for col:" + str(col)
                    # print "Reached here"
                    (next_board, score) = TetrisGame.place_piece((board, score), b.piece, row, col)
                    # print "Next board for calculating heuristics:"
                    # print next_board
                    # print "Original board after place piece:"
                    # print board
                    new_heuristic, new_row, new_col, new_rot = get_best_move(next_board, next_piece)
                    if new_heuristic >= max_heuristic:
                        max_heuristic = new_heuristic
                        min_row = row
                        min_col = col
                        min_rot = rotation
                    # print "Min row, col and rot" + str(row), str(col), str(rotation)
            rotation += 1
            # print "Rotation of current block:" + str(rotation)
            if debug == 1:
                print min_col, min_row, min_rot
            b.piece = TetrisGame.rotate_piece(b.piece, 90)

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
        # print "Moves: " + str(moves)
        # print max_heuristic, min_col, min_row, min_rot
        # print tetris.row - min_row
        # print tetris.col - min_col
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
        max_heuristic, min_col, min_row, min_rot = get_best_move(copy.deepcopy(tetris))
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
        i = 0
        current_piece = tetris.get_piece()
        # next_piece = tetris.get_piece()
        # print "Moves: " + str(moves)
        while 1:
            time.sleep(0.5)
            # for i in range(0, len(moves)):
            #     time.sleep(0.1)
            if i >= len(moves) and current_piece == tetris.get_piece():
                tetris.down()
            elif current_piece != tetris.get_piece():
                current_piece = tetris.get_piece()
                max_heuristic, min_col, min_row, min_rot = get_best_move(copy.deepcopy(tetris))
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
                i = 0
                # print "Moves: " + str(moves)
                sys.stdout.write("Moves: " + str(moves))

            elif moves[i] == 'b':
                tetris.left()
            elif moves[i] == 'm':
                tetris.right()
            elif moves[i] == 'n':
                tetris.rotate()
            else:
                tetris.down()
            i += 1

                # board = tetris.get_board()
                # column_heights = [min([r for r in range(len(board) - 1, 0, -1) if board[r][c] == "x"] + [100, ]) for c in
                #                   range(0, len(board[0]))]
                # index = column_heights.index(max(column_heights))
                # print column_heights
                # print index
                # if (index < tetris.col):
                #     tetris.left()
                # elif (index > tetris.col):
                #     tetris.right()
                # else:
                #     tetris.down()



    def control_game1(self, tetris):
        # another super simple algorithm: just move piece to the least-full column
        while 1:
            time.sleep(0.5)

            board = tetris.get_board()
            column_heights = [min([r for r in range(len(board) - 1, 0, -1) if board[r][c] == "x"] + [100, ]) for c in
                              range(0, len(board[0]))]
            index = column_heights.index(max(column_heights))
            # print column_heights
            # print index

            if (index < tetris.col):
                tetris.left()
            elif (index > tetris.col):
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

