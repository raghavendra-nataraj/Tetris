# Simple tetris program! v0.1
# D. Crandall, Sept 2016
import operator
from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
import time, sys

class HumanPlayer:
    def get_moves(self, piece, board):
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
    # Given a new piece (encoded as a list of strings) and a board (also list of strings), 
    # this function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. 
    #

    def get_height(self,board):
        count = 0
        for row in board:
            if row.strip()=='':
                count+=1
        return len(board)-count

    def get_aggr_height(self,board):
        hieghts = [0]*len(board[0])
        for index in range(len(board)-1,-1,-1):
            row = board[index]
            for rindex,item in enumerate(row):
                if item=='x':
                    hieghts[rindex]=len(board)-index
        bumpiness = [abs(hieghts[i]-hieghts[i-1]) for i in range(1,len(hieghts))]
        return sum(hieghts),sum(bumpiness)

    def get_holes(self,board):
        holes = 0
        encounter = [0]*len(board[0])
        for index,row in enumerate(board):
            for rindex,item in enumerate(row):
                if item=='x':
                    encounter[rindex] = 1
                if item==' ' and encounter[rindex]==1:
                    holes+=1
        return holes

    def lines_complete(self,board):
        count = 0
        for row in board:
            if row.count('x')==len(row):
                count+=1
        return count
        
    def get_row(self,board,col,piece):
        rowc = 0
        for row in board:
            if not TetrisGame.check_collision((board,0),piece,rowc+1,col):
                rowc+=1
            else:
                return rowc

    def calc_heuristics(self,board,row,col,piece):
        
        clf = 0.70666#0.9
        bf = -0.184483#-0.3
        hf =-0.35663 #-1.7
        ahf = -0.510066#-0.4
        agr_hieght,bumpiness = self.get_aggr_height(board)
        clear_lines = self.lines_complete(board)
        holes = self.get_holes(board)
        heuristic = (clf *clear_lines)  + (bf * bumpiness) + (ahf * agr_hieght) + (hf * holes) 
        #print clear_lines
        return heuristic
                
    def get_best_moves(self,tetris):
        board = tetris.get_board()
        piece = tetris.piece
        pieces = [TetrisGame.rotate_piece(piece,i) for i in [0,90,180,270]]
        heu = []
        for onep in pieces:
            for col in range(0,len(board[0])):
                row = self.get_row(board,col,onep)
                if row > 0:
                    #print col
                    #print self.get_aggr_height(board)
                    board1,score = TetrisGame.place_piece((board,0),onep,row,col)
                    h = self.calc_heuristics(board1,row,col,onep)
                    heu.append([row,col,onep,h])
        #print heu
        #print max(heu,key=operator.itemgetter(3))
        min_row,min_col,min_piece,h =  max(heu,key=operator.itemgetter(3))
        moves = ""
        turns = {0:"",90:"n",180:"nn",270:"nnn"}
        for i in [0,90,180,270]:
            #print piece,min_piece
            if TetrisGame.rotate_piece(piece,i) == min_piece:
                moves+=turns[i]
                break
        #print min_col
        if min_col>tetris.col:
            temp_moves = "m"*(min_col-tetris.col)
        else:
            temp_moves = "b"*(tetris.col-min_col)
        moves+=temp_moves
        return moves
                
        

    def get_moves(self, tetris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        #return random.choice("mnb") * random.randint(1, 10)
        moves = self.get_best_moves(tetris)
        #print moves
        #raw_input()
        return moves
       
    # This is the version that's used by the animted version. This is really similar to get_moves,
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



