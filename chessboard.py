import pyautogui as pag
import re
import time
import sys
from stockfish import Stockfish
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from random import randint

class Chess:
    cpri = "Copyright Grzegorz Libiszewski\nMiłego dnia"
    remaped_moves_key = {
        'e8h8': 'e8g8',
        'e8a8': 'e8c8',
        'e1h1': 'e1g1',
        'e1a1': 'e1c1'
    }
    moves = []
    is_moved = False
    wait = False
    started_black = False
    expir_fast = False




    def __init__(self, driver, params = None):
        self.driver = driver
        self.scrW, self.scrH = pag.size()
        def_params = {
        'mode': True,
        'wait': True,
        'next_match': True,
        'debug': False,
        'body_offset_height': None
        }
        if params is None:
            params = {}
        def_params.update(params)
        self.params = def_params
        if self.params['debug']: print(self.params)
        if self.params['body_offset_height'] == None:
            print('body_offset_height not found')
    def fetchBoard(self):
        self.board = self.driver.find_element_by_tag_name("cg-board")
        self.tab_pos = {}
        board_location = self.board.location
        self.board_size = self.board.size
        self.tab_pos['stack'] = {}
        self.tab_pos['stack']['width'] = self.tab_pos['stack']['height'] = int(self.board_size['width'] / 8)
        self.tab_pos['left_bottom'] = {}
        self.tab_pos['right_top'] = {}
        self.tab_pos['right_bottom'] = {}
        self.tab_pos['left_top'] = {}
        self.tab_pos['left_bottom']["x"] = int(board_location['x'])
        self.tab_pos['left_top']["x"] = int(board_location['x'])
        self.tab_pos['left_top']["y"] = int((self.scrH - self.params['body_offset_height']) + board_location['y'])
        self.tab_pos['right_top']["y"] = int((self.scrH - self.params['body_offset_height']) + board_location['y'])
        self.tab_pos['left_bottom']["y"] = int(self.tab_pos['left_top']["y"] + self.board_size['height'])
        self.tab_pos['right_bottom']["y"] = int(self.tab_pos['left_top']["y"] + self.board_size['height'])
        self.tab_pos['right_bottom']["x"] = int(board_location['x'] + self.board_size['width'])
        self.tab_pos['right_top']["x"] = int(board_location['x'] + self.board_size['width'])
        self.tab_pos['size'] = [self.board_size['width'], self.board_size['height']]
        self.determine_color()
    def printBoard(self):
        if not self.tab_pos:
            self.brdNtFnd()
        else:
            if self.params['debug']: print(self.tab_pos)

    def brdNtFnd(self):
        if self.params['debug']: print("Board was not found")

    def exit(self):
        print("\n"+self.cpri)
        sys.exit()
        

    def initEngine(self):
        self.moves = []
        self.stockfish = Stockfish(None, 10, {
            'Skill Level': 2500,
            'Threads': 4
        })
        self.stockfish.set_position([])
        self.fetchBoard()
        self.printBoard()


    def calc_position(self, elem):
        transform = re.findall("\((.*?)\)", elem.value_of_css_property("transform"))[0]
        splited = transform.split(", ")
        if self.started_black:
            x = chr(ord('h')-round(int(splited[len(splited) - 2]) / self.tab_pos['stack']['width']))
            y = 1 + round(int(splited[len(splited) - 1]) / self.tab_pos['stack']['height'])
        else:
            x = chr(ord('a')+round(int(splited[len(splited) - 2]) / self.tab_pos['stack']['width']))
            y = 8 - round(int(splited[len(splited) - 1]) / self.tab_pos['stack']['height'])
        return str(x)+str(y)

    def are_you_to_fast(self, timing, wait_for_move):
        if self.expir_fast:
            time.sleep(1)
            self.expir_fast = False
        elif wait_for_move:
            if timing > 40 and timing < 60:
                time.sleep(randint(1, 2)/2)
            elif timing <= 40 and timing > 30:
                time.sleep(randint(0, 1)/2)
            elif timing >= 60:
                time.sleep(3+randint(2, 8))
            elif timing > 15 and self.params['mode']:
                time.sleep(0.2)

    def get_moves(self):
        last_moves = self.driver.find_elements_by_class_name("last-move")
        if len(last_moves) == 2:
            ad_tomv = [self.calc_position(last_moves[1]), self.calc_position(last_moves[0])]
            add_to_moves =  ad_tomv[0] + ad_tomv[1]
            add_to_moves = self.remap_moves(add_to_moves)
            self.moves.append(add_to_moves)
        return self.moves

    def remap_moves(self, add_to_moves):
        for key, value in self.remaped_moves_key.items():
            if add_to_moves == key:
                return value
        return add_to_moves

    def get_best_move(self, moves_array):
        self.stockfish.set_position(moves_array)
        best_move = self.stockfish.get_best_move()
        if len(self.moves) > 0 and self.moves[len(self.moves)-1] in best_move:
            self.moves[len(self.moves)-1] = self.moves[len(self.moves)-1] + 'q'
            self.get_best_move(moves_array)
        else:
            return best_move

    def make_move(self):
        now_move = self.get_best_move(self.get_moves())
        if self.params['debug']: print(now_move)
        self.moves.append(now_move)
        if self.params['debug']: print(self.moves)
        one, two = now_move[0]+now_move[1], now_move[2]+now_move[3]

        move_from = {}
        move_to = {}
        if self.params['debug']: print("STR Black: ", self.started_black)
        if self.started_black:
            move_from['x'] = 7 - int(ord(one[0])-97)
            move_from['y'] =9 - int(one[1])
            move_to['x'] = 7 - int(ord(two[0])-97)
            move_to['y'] =9 - int(two[1])
        else:
            move_from['x'] = int(ord(one[0])-97)
            move_from['y'] = int(one[1])
            move_to['x'] = int(ord(two[0])-97)
            move_to['y'] = int(two[1])
        xx = self.tab_pos['left_bottom']['x']+move_from['x']*self.tab_pos['stack']['width'] + int(self.tab_pos['stack']['width'] / 2)
        yy = self.tab_pos['left_bottom']['y']-move_from['y']*self.tab_pos['stack']['height'] + int(self.tab_pos['stack']['height'] / 2)
        if self.params['debug']: print("From: %s - %s" % (xx, yy))
        self.are_you_to_fast(self.get_time(), self.params['wait'])
        pag.moveTo(xx,yy, 0.2)

        xx = self.tab_pos['left_bottom']['x']+move_to['x']*self.tab_pos['stack']['width'] + int(self.tab_pos['stack']['width'] / 2)
        yy = self.tab_pos['left_bottom']['y']-move_to['y']*self.tab_pos['stack']['height'] + int(self.tab_pos['stack']['height'] / 2)
        if self.params['debug']: print("To: %s - %s" % (xx, yy))
        pag.dragTo(xx, yy, 0.2)
        time.sleep(0.5)
        self.is_moved = True

    def get_time(self):
        if self.params['mode']:
            timer = self.driver.find_elements_by_css_selector('.time')[1]
            timing = timer.text.replace("\n", "").split('.')[0].split(":")
            czas = int(timing[0])*60 + int(timing[1])
            return czas
        return 0

    def determine_color(self):
        class_name = self.driver.find_elements_by_css_selector(".cg-wrap")[0].get_attribute('class')
        if 'orientation-black' in class_name:
            self.started_black = True
        else:
            self.started_black = False

    def wait_for_move(self):
        print(self.started_black)
        while True:
            if not self.params['mode']:
                try:
                    odl = self.driver.find_element_by_class_name('rclock-top').find_elements_by_css_selector("*")
                except NoSuchElementException:
                    odl = []
                except NoSuchWindowException:
                    self.exit()
            else:
                try:
                    odl = self.driver.find_elements_by_css_selector('.rclock.rclock-bottom.running')
                    if len(odl) == 0:
                        odl = self.driver.find_elements_by_css_selector('.expiration.expiration-bottom.bar-glider')
                        if len(odl) > 0: self.expir_fast = True
                except NoSuchElementException:
                    odl = []
            lengs = len(odl)
            if not self.params['mode']:
                if (lengs == 0 and self.is_moved == False):
                    break
                if (lengs > 0 and self.is_moved == True):
                    self.is_moved = False
            else:
                if lengs > 0:
                    self.is_moved = False
                    break
            button_to_new_opponent = self.driver.find_elements_by_css_selector('.follow-up a.fbt')
            if len(button_to_new_opponent) > 0 and self.params['next_match']:
                time.sleep(0.3)
                button_to_new_opponent[0].click()
                return self.params['next_match']
            time.sleep(0.5)
        return False