import configparser
import numpy as np
from matplotlib import pyplot as plt
from mss.windows import MSS as mss
from time import time, sleep
from os import listdir, system
from keyboard import is_pressed
import mouse
from lib.euclidean_algorithm.euclide import optimal_t, lcm

class Prize_selector:
    ### INITIALIZE VARIABLES
    ### Paths
    IMG_PATH = 'data'
    # setup configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    # screen resolution
    res = np.array((int(config['SYSTEM']['screen width']), int(config['SYSTEM']['screen height'])))
    resized_window = np.array([1300/900*res[1], 1300/900*res[0]])
    resized_window[resized_window > res] = res[resized_window > res]
    offset = np.ceil((res - resized_window) / 2) # 180
    # areas of the screen to capture
    wheels = [0,0,0,0,0] # top +20, height -40, left +20, width -40
    wheels[0] = {'left': int( res[0]/1920*256  + offset[0]), 'top': int(res[1]/1080*688 + offset[1]), 'width': int(res[0]/1920*177), 'height': int(res[1]/1080*148)}
    wheels[1] = {'left': int( res[0]/1920*473  + offset[0]), 'top': int(res[1]/1080*688 + offset[1]), 'width': int(res[0]/1920*177), 'height': int(res[1]/1080*148)}
    wheels[2] = {'left': int( res[0]/1920*690  + offset[0]), 'top': int(res[1]/1080*688 + offset[1]), 'width': int(res[0]/1920*177), 'height': int(res[1]/1080*148)}
    wheels[3] = {'left': int( res[0]/1920*907  + offset[0]), 'top': int(res[1]/1080*688 + offset[1]), 'width': int(res[0]/1920*177), 'height': int(res[1]/1080*148)}
    wheels[4] = {'left': int( res[0]/1920*1124 + offset[0]), 'top': int(res[1]/1080*688 + offset[1]), 'width': int(res[0]/1920*177), 'height': int(res[1]/1080*148)}
    # update button position
    update_pos = (int(res[0]/1920*1241 + offset[0]), int(res[1]/1080*607 + offset[1]))
    # server connection retry button position
    server_pos = (int(res[0]/2),int(res[1]/1080*600 + offset[1]))

    server_failure_sample = np.load(f'{IMG_PATH}\\wheel1\\server error.npy')
    # object for fast screenshots
    sct = mss()

    ### CONTEXT MANAGER METHODS ###

    def __enter__(self):
        self.cells = {}
        self.lengths = self._initialize_lengths()
        self.pos = np.zeros(5, np.int64)
        self.objective = np.zeros(5, np.int64)
        self.wait = float(self.config['Yearbook settings']['wait'])
        self._load_images()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('\nClosing...\n\n')
        self.sct.close()

    ### PROGRAM OPTIONS ###

    def run(self):
        while 1:
            system('cls')
            print(r". . __. __  _  _  _ . . .  .. . _ ___ ____ . .  __  _ . . ",
                r"\ //_/_\|_\|_\/ \/ \|/  |\/|\ //_' | |_ |_\\ /  |_\/ \\ / ",
                r" | \_| || \|_/\_/\_/|\, |  | | ._/ | |__| \ |   |_|\_// \ ",'prize selector\t\t\t\t\t\tby Dj Frixz',sep='\n')
            choice = int(input('\nSelect one option:\n\n0 - search\n1 - capture item1\n2 - capture item2\n...\n5 - capture item5\n'
                               '6 - select prizes\n7 - update n times\n8 - settings\n9 - quit\n\n'))
            if choice==0:
                if self._load_images() : self.ask_search()
            elif 0<choice<6: self.capture(choice-1)
            elif choice==6: self.select_prizes()
            elif choice==7: self.click_n_times(input('How many?\n'))
            elif choice==8: self.settings()
            elif choice==9: return
            elif choice==10: self.test()

    def test(self):
        print(self.find_match(self.cells, self.cells, False))
        for key in self.cells:
            print(key,':',self.similarity(self.cells[key],self.grab_screen(self.wheels[key])))
        a = input('\nPress <Enter> to continue... ')

    def ask_search(self):
        ans = input('Which method do you want to use? (enter blank to return) '
                    '\n\n0 - mathematical (recommended) '
                    '\n1 - image recognition (less reliable, faster for a single item search)\n\n')
        
        match ans:
            case '0':
                self.algebraic_search()
                self.lengths = self._initialize_lengths()
            case '1':
                self.standard_search()

    def _load_images(self) -> bool:
        self.cells = {}
        for i in range(5):
            item = self.config['Yearbook selection'][f'item{i+1}']
            if item!='':
                self.cells[i] = np.load(f'{self.IMG_PATH}\\wheel{i+1}\\{item}.npy')
        if len(self.cells)>0:
            return True
        else:
            print('Error: no prize is specified in the config.ini \n\nHint: to solve this issue try adding items and selecting them after choosing 6 in the menu.')
            self.pause()
            return False

    def standard_search(self, delay = 2):
        timeout = int(self.config['Yearbook settings']['timeout'])
        server_check = int(self.config['Yearbook settings']['server check'])
        sleep(delay)
        while 1:
            found = False
            t0 = t1 = time()
            while not ( found or is_pressed('space') or (time() - t0 > timeout) ):
                if time() - t1 >= server_check:
                    self.server_failure_check()
                    t1 = time()
                found = self.find_match(self.cells, self.cells)
            
            if found: print('A match has been found!')
            elif time() - t0 > timeout: print('Time over.')
            else: print('Search interrupted.')
            repeat = input('Retry? (y/n)\n')
            if repeat!='y':
                return
            print('Ok, starting in ',end='')
            self.countdown(delay)
    
    def algebraic_search(self):
        self.pos = np.zeros(5, np.int64)
        print('\nThe saved lengths are', self.lengths[np.sort(list(self.cells.keys()))])
        print('(Only wheels with a selected prize are considered)')
        if input('\nDo you want to recalculate them? (y/n)\n') == 'y':
            self.lengths = np.full(5, 1, np.int64)
            self.setup()
        else:
            self.setup(obj_only=True)
            
        clicks, i = self.calc_distance()

        if clicks == -1:
            print("The selected combination is not reachable.",i)
            self.pause()
            return
        
        print("You're {} clicks away from your objective.".format(clicks))
        if input("Do you wish me to do it for you? (y/n)\n")=='n':
            return
        self.click_n_times(clicks)
        
    def calc_distance(self) -> int:
        clicks = 0
        n0 = 1
        for i in range(self.lengths.size):
            t, lcm = optimal_t(self.objective[i] - self.pos[i] , n0, self.lengths[i])
            if t == -1:
                return -1, i
            n_steps = n0*t
            self.increment_pos(n_steps)
            clicks += n_steps
            n0 = lcm
        return clicks, clicks

    def increment_pos(self, n_steps):
        for i in range(self.pos.size):
            self.pos[i] = (self.pos[i] + n_steps) % self.lengths[i]
        # self.pos = (self.pos + arr) % self.lengths

    def setup(self, obj_only = False):
        sleep(2)
        start = {}
        for key in self.cells:
            start[key] = self.grab_screen(self.wheels[key])
        n = len(start)
        ended = 0
        ones = np.full(5, 1, np.int64)
        while ended<n:
            if is_pressed('space') or self.find_match(self.cells, self.cells):
                return
            self.pos += ones
            for key in ({0,1,2,3,4} - start.keys()):
                if self.pos[key] == self.lengths[key]:
                    self.pos[key] = 0
            erase = []
            for key in start:
                if self.find_match(start, (key,), False):
                    self.lengths[key] = self.pos[key]
                    self.pos[key] = 0
                    if not obj_only:
                        ended += 1
                        erase.append(key)
                if self.find_match(self.cells, (key,), False):
                    self.objective[key] = self.pos[key]
                    if obj_only:
                        ended += 1
                        erase.append(key)
            for key in erase:
                del start[key]
        
        if not obj_only:
            for i in self.cells:
                self.config['Yearbook selection'][f'length{i+1}'] = str(self.lengths[i])

        mask = np.sort(list(self.cells.keys()))
        self.lengths, self.objective, self.pos = self.lengths[mask], self.objective[mask], self.pos[mask]
        print('lengths:',self.lengths)
        print('objective:',self.objective)
        print('position:',self.pos)
        print('full cycle (total combinations):', lcm(self.lengths))
        
        self._save_config()
        self.pause()
    
    def capture(self,n):
        input('Prepare to alt-tab to the game window.\nWhen ready press <enter>.')
        print('Screenshot in ',end='')
        self.countdown(3)
        img = self.grab_screen(self.wheels[n])
        plt.imshow(img), plt.xticks([]), plt.yticks([])
        plt.show()
        ans = input('Insert name to save the image:\n(leave blank to cancel)\n')
        if ans!='':
            np.save(f"{self.IMG_PATH}\\wheel{n}\\{ans}.npy", img)

    def select_prizes(self):
        print('\nThese are the currently selected prizes:\n')
        for i in range(1,6):
            print(i,'-',self.config['Yearbook selection'][f'item{i}'])
        choice = int(input('\nWhich one do you want to change? (0 = nothing)\n'))
        if choice==0: return
        if choice<0 or choice>5:
            raise ValueError
        prizes = listdir(f'{self.IMG_PATH}\\wheel{choice}')
        if len(prizes)==0:
            print(f'\nThere are no prizes for slot {choice}, try adding one first.')
            return
        prizes = ['nothing.npy'] + prizes
        print('\nThese are the available prizes to select:\n\n')
        for i in range(len(prizes)):
            print(i,'-',prizes[i][:-4])
        i = int(input('\nChoose one:\n'))
        prize = prizes[i][:-4]
        if i==0:
            prize = ''
        if prize != self.config['Yearbook selection'][f'item{choice}']:
            self.config['Yearbook selection'][f'item{choice}'] = prize
            self.objective = np.zeros(5, np.int64)
            self._save_config()
            self._load_images()

    def click_n_times(self,times):
        for i in range(times):
            if is_pressed('space') or self.server_failure_check():
                if input("Stopped. Do you want to resume? (y/n)\n")=='n':
                    return
            self.mouse_click(self.update_pos, 0.1)
    
    def settings(self):
        seconds = int(self.config['Yearbook settings']['timeout'])
        print('\nChoose the setting you want to change:\n')
        print('1 - resolution (',self.config['SYSTEM']['screen width'],'x',self.config['SYSTEM']['screen height'],')')
        print('2 - wait time between clicks ( {} sec)\n3 - timeout ( {} sec ~ {} min )'.format(self.wait,seconds,int(seconds/60)))
        seconds = int(self.config['Yearbook settings']['server check'])
        print('4 - server check timeout ( {} sec ~ {} min )\n5 - return'.format(seconds,int(seconds/60)))
        n = int(input('\n'))
        if n==1:
            self.config['SYSTEM']['screen width'] = input('\nwidth: ')
            self.config['SYSTEM']['screen height'] = input('heigth: ')
            input("*The changes will take effect after restarting the program. Press <enter> to SAVE and continue.*")
        elif n==2:
            self.config['Yearbook settings']['wait'] = input('\nwait (seconds): ')
            self.wait = float(self.config['Yearbook settings']['wait'])
        elif n==3: 
            self.config['Yearbook settings']['timeout'] = float(input('\ntimeout (seconds): '))
        elif n==4:
            self.config['Yearbook settings']['server check'] = float(input('\nserver check timeout (seconds): '))
        else:
            return
        
        self._save_config()
    
    ### UTILITY

    def find_match(self, dict_, keys, click = True) -> bool:
        '''If a mismatch is found, the prizes are updated (shuffled) and False is returned, otherwise True.'''
        sensitivity = float(self.config['Yearbook settings']['sensitivity'])
        for key in keys:
            img = self.grab_screen(self.wheels[key])
            if self.similarity(img, dict_[key]) < sensitivity:
                if click: self.mouse_click(self.update_pos, 0, 0, self.wait)
                return False
        return True

    def similarity(self,img1:np.ndarray,img2:np.ndarray) -> float:
        '''Return the standardized sum of the absolute errors.'''
        return 1 - np.sum(np.abs(img1-img2))/(255*img2.size)

    def grab_screen(self,capture):
        '''Take a screenshot and return it as a numpy ndarray.'''
        return np.array(self.sct.grab(capture))[:,:,:3]

    def mouse_click(self,pos,duration=0.5,delay=0,wait=0):
        sleep(delay)
        mouse.move(pos[0],pos[1],duration=duration)
        mouse.click()
        sleep(wait)

    def countdown(self,n):
        for i in range(n,0,-1):
            print(i,end=' ')
            sleep(1)
        print('\n')
    
    def server_failure_check(self):
        sensitivity = float(self.config['Yearbook settings']['sensitivity'])
        img = self.grab_screen(self.wheels[0])
        if self.similarity(img,self.server_failure_sample) < sensitivity:
            return False
        while self.similarity(img,self.server_failure_sample) >= sensitivity and not is_pressed('space'):
            self.mouse_click(self.server_pos)
            sleep(10)
            self.mouse_click(self.server_pos)
            sleep(10)
            img = self.grab_screen(self.wheels[0])
        self.mouse_click((548, 226))
        self.mouse_click((1657, 1006))
        self.mouse_click((1045, 702))
        return True
    
    def pause(self):
        input('\nPress <Enter> to continue... ')

    def _initialize_lengths(self):
        return np.array((
            int(self.config['Yearbook selection']['length1']),
            int(self.config['Yearbook selection']['length2']),
            int(self.config['Yearbook selection']['length3']),
            int(self.config['Yearbook selection']['length4']),
            int(self.config['Yearbook selection']['length5'])
        ), np.int64)
    
    def _save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)



with Prize_selector() as program:
    program.run()
    # program.setup()