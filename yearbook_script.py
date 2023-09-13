import configparser
import numpy as np
from matplotlib import pyplot as plt
from mss.windows import MSS as mss
from time import time, sleep
from os import listdir
import mouse

### INITIALIZE VARIABLES
### Paths
IMG_PATH = 'data'
### Parts of the screen to capture ###
# screen resolution
def _init_screen():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['SYSTEM']['screen width']), int(config['SYSTEM']['screen height'])
width, height = _init_screen()
# areas to capture
wheels = [0,0,0,0,0,0]
wheels[1] = {'left': int(  613*width/3840), 'top':  int(1482*height/2160), 'width': int(  423*width/3840), 'height': int( 335*height/2160)}
wheels[2] = {'left': int( 1150*width/3840), 'top':  int(1482*height/2160), 'width': int(  461*width/3840), 'height': int( 335*height/2160)}
wheels[3] = {'left': int( 1653*width/3840), 'top':  int(1482*height/2160), 'width': int(  525*width/3840), 'height': int( 335*height/2160)}
wheels[4] = {'left': int( 1653*width/3840), 'top':  int(1482*height/2160), 'width': int(  525*width/3840), 'height': int( 335*height/2160)}
wheels[5] = {'left': int( 2762*width/3840), 'top':  int(1482*height/2160), 'width': int(  469*width/3840), 'height': int( 335*height/2160)}
# update button position
update_pos = (1539, 623)
# object for fast screenshots
sct = mss()

### FUNCTIONS

def main():
    while 1:
        print(r". . __. __  _  _  _ . . .  .. . _ ___ ____ . .  __  _ . . ",
              r"\ //_/_\|_\|_\/ \/ \|/  |\/|\ //_' | |_ |_\\ /  |_\/ \\ / ",
              r" | \_| || \|_/\_/\_/|\, |  | | ._/ | |__| \ |   |_|\_// \ ",'prize selector\t\t\t\t\t\tby Dj Frixz',sep='\n')
        choice = int(input('\nSelect one option:\n\n0 - start\n1 - capture item1\n2 - capture item2\n...\n5 - capture item5\n6 - select prizes\n9 - quit\n\n'))
        if choice==0: start()
        elif 0<choice<6: capture(choice)
        elif choice==6: select_prizes()
        elif choice==9: return
        else: raise ValueError

def start():
    config = configparser.ConfigParser()
    config.read('config.ini')
    cells = {}
    for i in range(1,6):
        item = config['Yearbook wheel selector'][f'item{i}']
        if item!='':
            cells[i] = np.load(f'{IMG_PATH}\\wheel{i}\\{item}.npy')
    if len(cells)>0:
        mainloop(cells)
    else: print('Error: no prize is specified in the config.ini')

def mainloop(cells, timeout=1000, delay = 2):
    sleep(delay)
    while 1:
        found = False
        t1 = time()
        while not ( found or mouse.is_pressed(mouse.MIDDLE) or (time() - t1 > timeout) ):
            found = shuffle(cells)
        if found: print('A match has been found!')
        elif time() - t1 > timeout: print('Time over.')
        else: print('Search interrupted.')
        repeat = input('Retry? (y/n)\n')
        if repeat!='y':
            return
        print('Ok, starting in ',end='')
        countdown(delay)
    
def shuffle(cells):
    for key in cells:
        img = grab_screen(wheels[key])
        if not are_similar(img, cells[key]):
            mouse_click(update_pos, 0, 0, 0.1)
            return False
    return True

def are_similar(img1:np.ndarray,img2:np.ndarray,threshold=0.1) -> bool:
    '''Returns True if the standardized sum of the absolute errors is less than threshold, otherwise returns False.'''
    return np.sum(np.abs(img1-img2))/(255*img2.size) < threshold

def capture(n):
    input('Prepare to alt-tab to the game window.\nWhen ready press <enter>.')
    print('Screenshot in ',end='')
    countdown(3)
    img = grab_screen(wheels[n])
    plt.imshow(img), plt.xticks([]), plt.yticks([])
    plt.show()
    ans = input('Insert name to save the image:\n(leave blank to cancel)\n')
    if ans!='':
        np.save(f"{IMG_PATH}\\wheel{n}\\{ans}.npy", img)
        config = configparser.ConfigParser()
        config.read('config.ini')
        config['Yearbook wheel selector'][f'item{n}'] = ans
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

def select_prizes():
    config = configparser.ConfigParser()
    config.read('config.ini')
    print('\nThese are the currently selected prizes:\n')
    for i in range(1,6):
        print(i,'-',config['Yearbook wheel selector'][f'item{i}'])
    choice = int(input('\nWhich one do you want to change? (0 = nothing)\n'))
    if choice==0: return
    if choice<0 or choice>5:
        raise ValueError
    prizes = listdir(f'{IMG_PATH}\\wheel{choice}')
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
    config['Yearbook wheel selector'][f'item{choice}'] = prize
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def grab_screen(capture):
    return np.array(sct.grab(capture))[:,:,:3]

def mouse_click(pos,duration=0.5,delay=0,wait=0):
    sleep(delay)
    mouse.move(pos[0],pos[1],duration=duration)
    mouse.click()
    sleep(wait)

def countdown(n):
    for i in range(n,0,-1):
        print(i,end=' ')
        sleep(1)
    print('\n')

main()
print('\nClosing...\n\n')
sct.close()