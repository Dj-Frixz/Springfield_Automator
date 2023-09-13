import cv2
import numpy as np
from matplotlib import pyplot as plt
#from mss import mss
from mss.windows import MSS as mss
from time import sleep
from os.path import join as path
import mouse

### PATHS
IMG_PATH = 'data'
### Parts of the screen to capture ###
# screen resolution
monitor = {"top": 0, "left": 0, "width": 3840, "height": 2160}
skip_pos = (1120, 220) #(448, 88)
ok_pos = (1913, 1358) #(765, 543)
# ratio = (1536, 864)
sct = mss()

def main():
    dollar = np.load(path(IMG_PATH,'dollar_symbol.npy'))
    money = np.load(path(IMG_PATH,'dollar_bill.npy'))
    register = np.load(path(IMG_PATH,'register.npy'))
    spray = np.load(path(IMG_PATH,'spray.npy'))
    menu = np.load(path(IMG_PATH,'menu.npy'))
    count = 0
    found = 0
    while not(mouse.is_pressed(mouse.RIGHT)):
        found += find_click(money)
        found += find_click(dollar)
        found += find_click(dollar)
        found += find_click(dollar)
        found += find_click(register)
        found += find_click(spray)
        found += find_click(spray)
        found += find_click(menu)
        
        if found >= 3 or count == 10:
            sleep(1)
            mouse_click(ok_pos)
            sleep(0.3)
            mouse_click(skip_pos)
            found = 0
            count = 0
            sleep(5)
        else:
            count += 1
            move_random()

def grab_screen(screen):
    return np.array(sct.grab(screen))[:,:,:3]

def mouse_click(pos,delay=0.5):
    mouse.move(pos[0],pos[1],duration=delay)
    mouse.click()

def move_random():
    i = np.random.random()
    n = 8
    if i<1/n:
        mouse.drag(2500,1000,500,1000,duration=0.3)
    elif i<2/n:
        mouse.drag(500,1000,2500,1000,duration=0.3)
    elif i<3/n:
        mouse.drag(1500,500,1500,1500,duration=0.4)
    elif i<4/n:
        mouse.drag(1500,1500,1500,500,duration=0.4)
    elif i<5/n:
        mouse.drag(1000,1000,3000,2000,duration=0.3)
    elif i<6/n:
        mouse.drag(2500,1500,500,500,duration=0.3)
    elif i<7/n:
        mouse.drag(500,1500,2500,500,duration=0.3)
    else:
        mouse.drag(2500,500,500,1500,duration=0.3)
    sleep(1)

def find_click(template,tolerance=0.9,duration=0.8,delay=0.5,screen=monitor):
    sleep(0.1)
    offset = np.array((template.shape[1]//2, template.shape[0]//2))

    # Get raw pixels from the screen, save it to a Numpy array
    img = grab_screen(screen)

    result = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    x = max_loc[0]+screen['left']+offset[0]
    y = max_loc[1]+screen['top']+offset[1]

    # tolerance is used to filter result
    if max_val>tolerance:
        mouse.move(x,y,duration=duration)
        mouse.click()
        sleep(delay)
        return True
    
    return False

main()
sct.close()