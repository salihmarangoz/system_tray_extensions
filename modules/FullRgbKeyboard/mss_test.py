import time
import cv2
import mss
import numpy

def test():
    sct = mss.mss()

    mon = sct.monitors[1]
    left = mon["left"] + int(mon["width"]*0.01)
    top = int(mon["height"]*0.0)
    right = mon["width"] - int(mon["width"]*0.01)
    lower = mon["height"]

    mon_ = (left, top, right, lower)
    print(mon_)
    
    last_time = time.time()

    while True:
        img = numpy.asarray(sct.grab(mon_))

        width = 18
        height = 6
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        imS = cv2.resize(resized, (18*50, 6*50), interpolation = cv2.INTER_NEAREST) 
        cv2.imshow("test", imS)

        if cv2.waitKey(1000//60) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

test()