import pyautogui as pag
import time
import sys
from selenium.webdriver.common.keys import Keys
import getpass
import os.path
import json

class Logger:

    CREDENTIALS_FILE_NAME = 'credentials.txt'

    def __init__(self, driver, debug = False):
        self.driver = driver
        self.debug = debug
    
    def login(self):
        login_params = {}
        if not os.path.isfile(self.CREDENTIALS_FILE_NAME):
            file = open(self.CREDENTIALS_FILE_NAME, 'w')
            login_params['username'] = input("Type your lichess username: ")
            pssw = getpass.getpass("Type your password, if you don't want to store your password click enter: ")
            if pssw != '': login_params['password'] = pssw
            file.write(json.dumps(login_params))
            file.close()
        else:
            file = open(self.CREDENTIALS_FILE_NAME, "r")
            read_file = json.loads(file.read())
            login_params = read_file
            file.close()
        log_button = self.driver.find_elements_by_css_selector('.signin.button.button-empty')
        is_logged = True if len(log_button) == 0 else False
        if is_logged:
            return True
        self.driver.get('https://lichess.org/login')
        username_filed = self.driver.find_element_by_id('form3-username')
        username_filed.send_keys(login_params['username'])
        password_filed = self.driver.find_element_by_id('form3-password')
        password_filed.send_keys(getpass.getpass("Type password: ") if not 'password' in login_params or login_params['password'] == '' else login_params['password'])
        password_filed.send_keys(Keys.ENTER)
        while True:
            if self.driver.current_url.split('/')[3] == '':
                break
            elif len(self.driver.find_elements_by_css_selector('.error')) > 2:
                print("Can't login, invalid username or password")
                sys.exit()
            time.sleep(1)
        return True
