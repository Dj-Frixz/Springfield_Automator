import cv2
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import mouse
#directKeys

image = cv2.imread("screen7.png",0)
template = cv2.imread("thumb_up3.png",0)
h,w = template.shape

result = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
#min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#print(min_val, max_val, min_loc, max_loc, template.shape)
#top_left = max_loc
#bottom_right = (top_left[0] + w, top_left[1] + h)
#cv2.rectangle(image,top_left, bottom_right, 255, 2)
#plt.subplot(121),plt.imshow(result,cmap = 'gray')
#plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
#plt.subplot(122),plt.imshow(image,cmap = 'gray')
#plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
#plt.suptitle("TM_CCOEFF")
#plt.show()
y,x = np.unravel_index(result.argmax(),result.shape)
#print(x,y,result.shape[1],result.shape[0])
sleep(2)
mouse.move(x,y,duration=1)
sleep(2)
mouse.click()
