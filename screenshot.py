from mss import mss
from time import sleep
from matplotlib import pyplot as plt
import numpy as np

sct = mss()
window = {'left':747, 'top':144, 'width':85, 'height':20}

sleep(2)
#img = sct.grab(window)
#np.save(r'data\window_border.npy',img)
img1 = sct.grab(window)
img2 = np.load(r'data\window_border.npy')
print(np.array_equal(img1,img2))
plt.subplot(121),plt.imshow(img1)#,cmap = 'gray')
plt.title('Screenshot'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(img2)
plt.title('Saved Image'), plt.xticks([]), plt.yticks([])
plt.suptitle("BRUH")
plt.show()