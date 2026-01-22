
from chessvision import Chessvision
from engine_game import LichessGame


token = "-- INSERT YOUR LICHESS TOKEN --"
vision = Chessvision()
game = LichessGame(token)
game.start_game(8)


input("Play move: ")
move = vision.capture_and_get_move()
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

                # update internal board tracking
                vision.board_manager.play_move(move_played) 
                vision.capture_and_update_last_board_state()
                        
                white_move = False
                promotion = input("Play move: ")

                move = vision.capture_and_get_move()

                if promotion:
                    move += promotion

                game.play_move(move)
            else:
                print("white played: ", move_played)
                white_move = True
        else:
            print("Game ended")
    i = 1

