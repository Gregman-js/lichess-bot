import pyautogui as pag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class Runway:

    GAME_MODE_FAST = 0
    GAME_MODE_USER = 1
    GAME_MODE_COMPUTER = 2
    game_property = {}
    game_url = ''

    def __init__(self, params = None):
        self.scrW, self.scrH = pag.size()
        def_params = {
        'next_match': True,
        'play_with': self.GAME_MODE_COMPUTER,
        'comp_lvl': 8,
        'comp_white': True,
        'debug': False
        }
        if params is None:
            params = {}
        def_params.update(params)
        self.params = def_params

    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("http://lichess.org")
        self.body_offset_height = int(self.driver.execute_script("return window.innerHeight"))
        self.game_property['next_match'] = self.params['next_match']
        self.game_property['debug'] = self.params['debug']
        self.game_property['body_offset_height'] = self.body_offset_height

    def lets_play(self):
        if self.params['play_with'] == self.GAME_MODE_FAST:
            self.click_fast_game()
        elif self.params['play_with'] == self.GAME_MODE_USER:
            self.click_user()
        else:
            self.click_computer(self.params['comp_lvl'], self.params['comp_white'])
        self.wait_for_go()
        pag.click(10, self.scrH / 2)

    def wait_for_go(self):
        while True:
            if self.driver.current_url.split('/')[3] != '' and self.driver.current_url.split('/')[3] != self.game_url:
                self.game_url = self.driver.current_url.split('/')[3]
                break
            time.sleep(1)

    def click_fast_game(self):
        quick_pair_tab = self.driver.find_element_by_css_selector('.tabs-horiz')
        quick_pair_tab.find_elements_by_css_selector("*")[0].click()
        time.sleep(0.2)
        button = self.driver.find_element_by_css_selector('.lobby__app__content.lpools')
        button.find_elements_by_css_selector("*")[1].click()
        time.sleep(0.2)
        self.game_property['mode'] = True
        self.game_property['wait'] = True

    def click_computer(self, eight, white = True):
        self.driver.find_element_by_css_selector('.button.button-metal.config_ai').click()
        time.sleep(0.3)
        if eight:
            self.driver.execute_script("document.getElementById('sf_level_"+str(eight)+"').click()")
            time.sleep(0.3)
        self.driver.find_element_by_css_selector('.color-submits__button.button.button-metal.'+('white' if white else 'black')).click()
        time.sleep(0.4)
        self.game_property['mode'] = False
        
    def click_user(self):
        self.driver.find_element_by_css_selector('.button.button-metal.config_hook').click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('button.color-submits__button.button-metal.white').click()
        time.sleep(0.5)
        self.game_property['mode'] = True
        self.game_property['wait'] = True

    def get_params(self):
        if self.params['debug']: print(self.game_property)
        return self.game_property
    def get_driver(self):
        return self.driver