# import cv2
#
# cap = cv2.VideoCapture(0)
# import matplotlib.pyplot as plt
#
# # cap.set(cv2.CV_CAP_PROP_FRAME_WIDTH , 352);
# # cap.set(cv2.CV_CAP_PROP_FRAME_HEIGHT , 288);
#
# ret, frame = cap.read()


import sys, os
# import PIL
import cv2

# cap = cv.CreateCameraCapture(0)
cap = cv2.VideoCapture(0)
print cap.isOpened()
# cap.open()
# cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_WIDTH, 640)
# cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_HEIGHT, 480);
print cap.get(3)
print cap.get(4)

if not cap:
    print "Error opening WebCAM"
    sys.exit(1)

ret, frame = cap.read()

# frame = cv.QueryFrame(camcapture)
# cv.ShowImage('Camera', frame)
