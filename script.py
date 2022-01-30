import cv2
import numpy as np
#from matplotlib import pyplot as plt
from mss import mss
from time import sleep
from os.path import join as path
import mouse
#directKeys

sct = mss()
IMG_PATH = 'data'
prec_val = 0
repetition = False

### Parts of the screen to capture ###
# screen resolution
monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
# left side of the screen
left_side = {'left':0, 'top':0, 'width':829, 'height':1080}
# right side of the screen
right_side = {'left':1039, 'top':0, 'width':881, 'height':1080}
# in-game window
window = {'left':633, 'top':214, 'width':672, 'height':548}
# in-game window border (not really, more of a recognisable part of the border)
window_border = {'left':750, 'top':144, 'width':85, 'height':20}
######################################

def find_click(template,tolerance=35000000,duration=0.8,delay=0.5,screen=monitor):
    sleep(0.1)
    offset = np.array((template.shape[1]//2, template.shape[0]//2))

    # Get raw pixels from the screen, save it to a Numpy array
    img = np.array(sct.grab(screen))#cv2.COLOR_RGB2BGR)
    #cv2.imwrite("img.png",img)
    #cv2.imwrite("templ.png",template)
    #print(img.shape)
    #print(template.shape)

    # cv2.imshow("Test",img)
    result = cv2.matchTemplate(img,template,cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #print(min_val, max_val, min_loc, max_loc, template.shape)
    x = max_loc[0]+screen['left']+offset[0]
    y = max_loc[1]+screen['top']+offset[1]

    # not working function below
    # np.unravel_index(match,result.shape)

    # some shit useful for tests
    '''bottom_right = (top_left[0] + offset[0], top_left[1] + offset[1])
    cv2.rectangle(img,top_left, bottom_right, 255, 2)
    plt.subplot(121),plt.imshow(result,cmap = 'gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(img)
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle("TM_CCOEFF")
    plt.show()
    print(max_val)'''
    
    # tolerance is used to filter result
    if max_val>tolerance:
        #y,x = np.unravel_index(match,result.shape)#+offset
        #print("Found at %f %f"%(x/1920*100,y/1080*100))
        global prec_val,repetition
        repetition = max_val==prec_val
        prec_val = max_val
        mouse.move(x,y,duration=duration)
        mouse.click()
        sleep(delay)
        return True

    #if cv2.waitKey(1) & 0xFF == ord("q"):
    #    cv2.destroyAllWindows()
    #    break
    # sleep(2)

    # no correspondences
    return False

thumb = np.load(path(IMG_PATH,'thumb_up.npy'))
hammer = np.load(path(IMG_PATH,'hammer.npy'))
work = np.load(path(IMG_PATH,'work.npy'))
#image = cv2.imread("screen7.png",0)
#result = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
#print(result.argmax())

def send_to_work():
    found = False
    for i in range(6):
        if not(find_click(work,tolerance=25000000,duration=0.2,screen=window)):
            break
        found = True
    
    global window_border,repetition
    if np.array_equal(sct.grab(window_border),np.load(path(IMG_PATH,'window_border.npy'))):
        # close the in-game window clicking on the exit arrow on the top-left
        mouse.move(window['left'],window['top'],duration=0.2)
        mouse.click()
        sleep(0.5)
        repetition = not(found)
    else:
        repetition = False

while not(mouse.is_pressed(mouse.RIGHT)):
    sleep(1)
    find_click(thumb,delay=2)
    if repetition:
        if find_click(hammer,23000000,delay=0.5,screen=left_side):
            send_to_work()
        if repetition:
            if find_click(hammer,23000000,delay=0.5,screen=right_side):
                send_to_work()
    else:
        if find_click(hammer,23000000,delay=0.5):
            #print("Found!")
            send_to_work()
    #print("--new loop--")