import requests
import json
import sys






class LichessGame:
    def __init__(self, token):
        self.header = {
            'Authorization': 'Bearer ' + token
        }

        self.gameid = None
    
    def start_game(self, level):
        params = {
                    'level': level,
                    'days': 1,
                    'color': 'white',
                    'variant': 'standard'
                }

        game_start_url = "https://lichess.org/api/challenge/ai"

        game_start_r = requests.post(url=game_start_url, data=params, headers=self.header)
        data = game_start_r.json()
        print(game_start_r.status_code)
        self.gameid = data['id']
        print(f"Game started with ID: {self.gameid}")



    def play_move(self, move):
        if self.gameid == None:
            print("Cannot play move. No game started.")
            return


        if move == 'r':
            resign_game_url = f"https://lichess.org/api/board/game/{self.gameid}/resign"
            requests.post(url=resign_game_url, headers=self.header)
            print("You lost nigga.")
            return
        play_move_url = f"https://lichess.org/api/board/game/{self.gameid}/move/{move}"
        play_move_r = requests.post(url=play_move_url, headers=self.header)
        data = play_move_r.json()
        print(data)
        if play_move_r.status_code == 400:
            print("Resigning game...")
            resign_game_url = f"https://lichess.org/api/board/game/{self.gameid}/resign"
            requests.post(url=resign_game_url, headers=self.header)

    def stream_game_moves(self):
        if self.gameid == None:
            print("Cannot stream moves. No game started")
            return
        
        stream_game_url = f"https://lichess.org/api/board/game/stream/{self.gameid}"
        r = requests.get(stream_game_url, headers=self.header, stream=True)
        for line in r.iter_lines():
            if line:
                decoded_r = json.loads(line.decode('utf-8'))
                yield decoded_r


    
    


if __name__ == '__main__':

    token = "-- INSERT YOUR LICHESS TOKEN --"

    game = LichessGame(token)
    game.start_game(8)


    move = input("Play move: ")
    game.play_move(move)
    i = 0
    white_move = True

    for event in game.stream_game_moves():
        if i:
            if(event['status']) == 'started':
                # print(x['moves'])
                print("=====================================")
                move_played = event['moves'][-4:]
                if white_move:
                    print("black played: ", move_played)
                    white_move = False
                    move = input("Play move: ")
                    game.play_move(move)
                else:
                    print("white played: ", move_played)
                    white_move = True

            else:
                print("Game ended")
        i = 1

    # stream_game_url = f"https://lichess.org/api/board/game/stream/{game.gameid}"
    # move = input("Play move: ")
    # game.play_move(move)
    # i = 0
    # white_move = True
    # with requests.get(stream_game_url, headers=game.header, stream=True) as resp:
    #     for line in resp.iter_lines():
    #         if line:
    #             if i:
    #                 x = json.loads(line.decode('utf-8'))
    #                 if(x['status']) == 'started':
    #                     # print(x['moves'])
    #                     print("=====================================")
    #                     move_played = x['moves'][-4:]
    #                     if white_move:
    #                         print("black played: ", move_played)
    #                         white_move = False
    #                         move = input("Play move: ")
    #                         game.play_move(move)
    #                     else:
    #                         print("white played: ", move_played)
    #                         white_move = True
                        
    #                 else:
    #                     print("Game ended")
    #             i = 1
    #     resp.close()