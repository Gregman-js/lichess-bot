from chessboard import *
from runway import *
from logger import *
import time
import sys

cpri = "Copyright Grzegorz Libiszewski\nMiłego dnia"
error_message = "Wystąpił poważny błąd"

params = {
        'next_match': False,
        'play_with': Runway.GAME_MODE_FAST,
        'comp_lvl': 1,
        'comp_white': True,
        'debug': False
        }
try:
    runway = Runway(params)
    runway.run()
    logger = Logger(runway.get_driver())
    if not logger.login():
        print("\nCan't login")
        sys.exit()
    runway.lets_play()
    chess = Chess(runway.get_driver(), runway.get_params())
    chess.initEngine()
    while True:
        new = chess.wait_for_move()
        if new:
            chess.initEngine()
            chess.wait_for_move()
        time.sleep(0.05)
        chess.make_move()

except (KeyboardInterrupt, EOFError):
    print('\n'+cpri)
# except:
#     print('\n'+error_message+'\n'+cpri)
