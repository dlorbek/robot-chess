import requests
import json
import numpy as np
from time import sleep
import sys
from move import MoveCommander
import pickle


ROBOT_MOVE_DELAY_S = 0.001

def moveL():
    sleep(ROBOT_MOVE_DELAY_S)


class BoardManager:
    def __init__(self):
        '''

        a8 ........ h8
        .
        .
        .
        .
        a1 ........ h1

        '''
        self.board = np.zeros(shape=(8, 8))
        self.board[0:2,:] = -1
        self.board[6:,:] = 1
        self.board = self.board.astype(int)

        self.black_can_castle = True
        self.white_can_castle = True
        
        self.WHITE_MOVE = 1
        self.BLACK_MOVE = 0
        self.has_move = self.WHITE_MOVE
        
        self.KINGSIDE = 'g'
        self.QUEENSIDE = 'c'
        
        
        self.mover = MoveCommander()
        
        with open('chessboard_config.pickle', 'rb') as file:
        # Load the object from the file
            loaded_data = pickle.load(file)
    
    
    
        self.bord = self.mover.chessboard(loaded_data[0], loaded_data[1], loaded_data[2])
        with open('home_config.pickle', 'rb') as file:
        # Load the object from the file
            self.home = pickle.load(file)
        
        self.mover.moveJ(self.home)
    

    def get_chessboard(self, T1, T2, T3):
        A1H1 = T2 - T1
        H1H8 = T3 - T2
        chessbord = {}
        
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        for i,f in enumerate(files):
            for r in ranks:
                chessbord[f+r] = T1 + A1H1/7*(int(r)-1) + H1H8/7*i

        return chessbord
    
    def is_occupied(self, square):
        return np.abs(self.board[7-(int(square[1])-1)][ord(square[0])-97])
    
    def update_board_state(self, move):
        first_pos = move[0:2]
        second_pos = move[2:]
        
            
        self.board[7-(int(first_pos[1])-1)][ord(first_pos[0])-97] = 0
        if self.has_move == self.WHITE_MOVE:
            self.board[7-(int(second_pos[1])-1)][ord(second_pos[0])-97] = 1
            if self.white_can_castle and second_pos[0] == self.KINGSIDE:
                self.board[7-(int('1')-1)][ord('h')-97] = 0
                self.board[7-(int('1')-1)][ord('f')-97] = 1
            elif self.white_can_castle:
                self.board[7-(int('1')-1)][ord('a')-97] = 0
                self.board[7-(int('1')-1)][ord('d')-97] = 1
            self.has_move = self.BLACK_MOVE
        else:
            self.board[7-(int(second_pos[1])-1)][ord(second_pos[0])-97] = -1
            if self.black_can_castle and second_pos[0] == self.KINGSIDE:
                self.board[7-(int('8')-1)][ord('h')-97] = 0
                self.board[7-(int('8')-1)][ord('f')-97] = -1
            elif self.black_can_castle:
                self.board[7-(int('8')-1)][ord('a')-97] = 0
                self.board[7-(int('8')-1)][ord('d')-97] = -1
            self.has_move = self.WHITE_MOVE
        
    
    def print_board_state(self):
        print(self.board)

    def take_piece(self, square):
        if not self.is_occupied(square):
            print("No piece to take.")
            return
        
        print("Taking piece...")
        
        second_pose = self.bord[square]
        self.mover.move_piece(second_pose, self.mover.offset(second_pose, 0.1, 0, 0.2))
        
    
    def castle(self, side):
        if self.has_move == self.WHITE_MOVE:
            if side == self.KINGSIDE:
                self.mover.move_piece(self.bord['e1'], self.bord['g1'])
                self.mover.move_piece(self.bord['h1'], self.bord['f1'])
            else:
                self.mover.move_piece(self.bord['e1'], self.bord['c1'])
                self.mover.move_piece(self.bord['a1'], self.bord['d1'])
        else:
            if side == self.KINGSIDE:
                self.mover.move_piece(self.bord['e8'], self.bord['g8'])
                self.mover.move_piece(self.bord['h8'], self.bord['f8'])
            else:
                self.mover.move_piece(self.bord['e8'], self.bord['c8'])
                self.mover.move_piece(self.bord['a8'], self.bord['d8'])
        
        

    def play_move(self, move):
        if (move[0:2] == 'a1' or move[0:2] == 'h1') and self.white_can_castle:
            self.white_can_castle = False
        if (move[0:2] == 'a8' or move[0:2] == 'h8') and self.black_can_castle:
            self.black_can_castle = False
        
        
        if move[0:2] == 'e1' and self.white_can_castle:
            
            if move[2:] == 'g1' or move[2:] == 'c1':
                self.castle(move[2])
                self.update_board_state(move)
                self.white_can_castle = False
                return
            else:
                self.white_can_castle = False
                print("White cannot castle anymore")
            

        if move[0:2] == 'e8' and self.black_can_castle:
            
            if move[2:] == 'g8' or move[2:] == 'c8':
                self.castle(move[2])
                self.update_board_state(move)
                self.black_can_castle = False
                return
            else:
                self.black_can_castle = False
                print("Black cannot castle anymore")
            
                

        if self.is_occupied(move[2:]):
            self.take_piece(move[2:])
        
        print("Playing move: " + move)
        self.update_board_state(move)
        self.mover.move_piece(self.bord[move[0:2]], self.bord[move[2:]])
        self.mover.moveJ(self.home)
    











if __name__ == "__main__":

    # gameID = "PRqhOVFbE4Hr"
    token = "lip_0Ts77SV8cBaivVT710ta"
    board = BoardManager()

    header = {
        'Authorization': 'Bearer ' + token
    }

    r = requests.get("https://lichess.org/api/account/playing", headers=header)
    data = r.json()
    data = data['nowPlaying']
    data_dict = dict(data[0])
    
    
    gameID = data_dict['gameId']
    url = "https://lichess.org/api/board/game/stream/" + gameID

    
    

    

    i = 0
    print("Game started")
    with requests.get(url, headers=header, stream=True) as resp:
        for line in resp.iter_lines():
            if line:
                if i:
                    x = json.loads(line.decode('utf-8'))
                    if(x['status']) == 'started':
                        board.play_move(x['moves'][-4:])
                        print("================================================")
                    else:
                        print("Game ended")
                i = 1
        resp.close()
    
    board.print_board_state()