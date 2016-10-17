# Simple Tetris implemented with max_heuristic and updated code for emptiness
# Simple tetris program! v0.2
# D. Crandall, Sept 2016
''' 1. Abstraction for problem 2:
a. Valid State, S: Any arrangement of pieces on a 20*10 board with a piece falling from top
b. Initial state, S0: Empty board one piece and score 0
c. Goal State, G: {S| S such that maximum lines are cleared from the board, i.e., achieve the highest possible score before the board fills up}
d. Successor function, Succ(S) = {S' | S' is a list of boards with the falling piece rotated in all possible ways and placed in all possible places on the current board}
e. Cost Function = The cost function is not much of a factor here since we will either reach or lose the game. So we can keep it a constant, i.e., one for each piece kept on the board
f. Heuristic function defined: The heuristic function used in the program is based on below 4 things -
(i) The increase in the aggregated height of the board after a given piece is placed on the board
(ii) The total number of holes created in the board after a given piece is placed on the board
(iii) The sum of difference in heights of the adjacent columns after a given piece is placed on the board
(iv) The number of completed lines, i.e., lines that will be cleared and added to the score, after a given piece is placed on the board.

All these 4 factors are assigned some weight based on how much they contribute in improving the score. The above 3 factors are assigned negative weights since they would reduce the score whereas completed lines would contribute in getting a higher score. The sum of all these weighted factors gives the final heuristic value. The one with the highest heuristic value is then selected to select the best possible successor board.

2. Description of how the program works:
The basic idea implemented in the algorithm is to use the A* search and select the best possible place for keeping a current piece. It first takes the current board and then checks every available position in each column for collision with the current piece. It selects the row which is just above the one where the first collision is found for each column. In this way, the algorithm finds a possible spot in each of the possible columns to keep the current piece (for all possible rotations of the piece).
Next, it checks for the non-colliding position in the same way for the next piece in the board which is a copy of the original board and has the current piece placed in one of the above found non-colliding positions. Using this board, it calculates the heuristics (explained in point 1) for each of the possible successor boards. It then selects the position for the current piece based on the highest heuristic value obtained after keeping both the current and next piece on the copy of the current board.

The animated version is implemented in a similar way except that it checks for the best possible position after making each move, i.e., after each left, right or rotation of the piece.

3. Problems faced and design decision made:
The main problem that we faced in implementing the algorithm was deciding the weights for each of the four factors of the heuristic function. For this, we did test our code with various combinations of weights. Sometimes, the program ran endlessly giving high scores whereas sometimes it would end giving a low score. Thus, we did testing and came up with the final weight combinations that gave a high score on an average in 5 runs.

The idea of the above heuristics was inspired from the below:
https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/

'''


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

def heuristic_height_diff(board):
    height = get_height(board)
    # print "In heuristic height"
    # print board
    agg_ht = 0
    for h in range(0, len(height)):
        agg_ht += height[h]
    return agg_ht


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


def get_heuristic((board, score), curr_max_ht):
    # print "Board in get heuristics:"
    # print board
    # print "\n" * 3 + ("Score: %d \n" % score) + "|\n".join(board) + "|\n" + "-" * 10
    height = get_height(board)
    new_max_ht = max(height)
    ht_diff = abs(new_max_ht - curr_max_ht)
    ht = -0.3
    emptiness = -0.4
    holes = -1.7
    clear_lines = 0.9
    heuristic = (ht * heuristic_height(board)) + (emptiness * heuristic_emptiness(board)) + \
           (holes * heuristic_holes(board)) + (clear_lines * heuristic_complete(board))

    # heuristic = (ht * ht_diff) + (emptiness * heuristic_emptiness(board)) + \
    #        (holes * heuristic_holes(board)) + (clear_lines * heuristic_complete(board))

    # heuristic = (d * heuristic_complete(board)) -((ht * ht_diff) + (emptiness * heuristic_emptiness(board)) + \
    #             (holes * heuristic_holes(board)) )
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

def get_best_move(board, piece, curr_max_ht):
    # board = b.get_board()
    score = 0
    max_heuristic = -8000
    min_col = 21
    min_row = 21
    min_rot = 0
    rot_pieces = []
    if debug == 1:
        print len(board)
    rotation = 0
    # height = get_height(board)
    # new_max_ht = max(height)
    # height_diff = abs(new_max_ht - curr_max_ht)
    while rotation < 3:
        if piece not in rot_pieces:
            rot_pieces.append(piece)
            for col in range(0, 10):
                # row = (19 - height[col]) - len(piece) + 1
                row = get_best_row(board, score, piece, col)
                if row > 0:
                    # print "Best Row for next piece: " + str(row) + " calculated for col:" + str(col)
                    new_heuristic = get_heuristic(TetrisGame.place_piece((board, score), piece, row, col), curr_max_ht)
                    # print "After place piece: "
                    # print board
                    if new_heuristic > max_heuristic:
                        max_heuristic = new_heuristic
                        min_row = row
                        min_col = col
                        min_rot = rotation

        rotation += 1
        # print "Rotation of next block:" + str(rotation)
        piece = TetrisGame.rotate_piece(piece, 90)
    # print "Next piece rotations:" + str(rot_pieces)
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
        height = get_height(board)
        curr_max_ht = max(height)
        rot_pieces = []
        # rot_pieces.append(b.piece)
        while (rotation < 3):
            # Run below for each piece rotation and each possible position of the current piece
            if b.piece not in rot_pieces:
                rot_pieces.append(b.piece)
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
                        new_heuristic, new_row, new_col, new_rot = get_best_move(next_board, next_piece, curr_max_ht)
                        if new_heuristic > max_heuristic:
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

        # print "Current piece rotations:" + str(rot_pieces)
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
        moves = []
        while 1:
            time.sleep(0.1)
            board = tetris.get_board()
            moves = self.get_moves(tetris)
            if len(moves) > 0:
                i = moves[0]
                if i == 'b':
                    tetris.left()
                elif i == 'm':
                    tetris.right()
                elif i == 'n':
                    tetris.rotate()
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

