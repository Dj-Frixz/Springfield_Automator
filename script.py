import cv2
import numpy as np
#from matplotlib import pyplot as plt
from mss import mss
from time import sleep
import mouse
#directKeys

sct = mss()
PATH = 'data'

# Part of the screen to capture
monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

def find_click(template,tolerance=40000000,duration=0.8,delay=0.5,screen=monitor):
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

# 1257, 745
window = {'left':633, 'top':214, 'width':672, 'height':548}

thumb = cv2.imread(f"{PATH}thumb_up3.png",cv2.IMREAD_UNCHANGED)
hammer = cv2.imread(f"{PATH}hammer.png",cv2.IMREAD_UNCHANGED)
work = cv2.imread(f"{PATH}work.png",cv2.IMREAD_UNCHANGED)
#image = cv2.imread("screen7.png",0)
#result = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
#print(result.argmax())

def send_to_work():
    for i in range(6):
        if not(find_click(work,tolerance=20000000,duration=0.2,screen=window)):
            break
    mouse.move(window['left'],window['top'],duration=0.2)
    mouse.click()
    sleep(0.5)

while not(mouse.is_pressed(mouse.RIGHT)):
    sleep(1)
    find_click(thumb,delay=2)
    if find_click(hammer,20000000,delay=0.5):
        print("Found!")
        send_to_work()
    #print("--new loop--")