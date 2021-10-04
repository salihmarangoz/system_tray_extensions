
"""
Visualizes video on the screen showing how it would look on the keyboard
Usage: python3 video_play.py input.mp4
"""


import cv2
import sys

cap = cv2.VideoCapture(sys.argv[1])
if(cap.isOpened() == False):
    print("Error Opening Video Stream Or File")

scale = 30
dim1 = (18, 6)
dim2 = (18*scale, 6*scale)

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break

    img = cv2.resize(frame, dim1, interpolation = cv2.INTER_NEAREST)
    img = cv2.resize(img, dim2, interpolation = cv2.INTER_NEAREST)

    if ret == True:
        cv2.imshow('frame', img)
        if cv2.waitKey(25)  == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()