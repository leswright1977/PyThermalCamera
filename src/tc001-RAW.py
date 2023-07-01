#!/usr/bin/env python3


import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()
	
if args.device:
	dev = args.device
else:
	dev = 0
	

#init video
cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
#cap = cv2.VideoCapture(0)

#we need to set the resolution here why?
'''
wright@CF-31:~/Desktop$ v4l2-ctl --list-formats-ext
ioctl: VIDIOC_ENUM_FMT
	Index       : 0
	Type        : Video Capture
	Pixel Format: 'YUYV'
	Name        : YUYV 4:2:2
		Size: Discrete 256x192
			Interval: Discrete 0.040s (25.000 fps)
		Size: Discrete 256x384
			Interval: Discrete 0.040s (25.000 fps)
'''

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
font=cv2.FONT_HERSHEY_SIMPLEX

while(cap.isOpened()):
	# Capture frame-by-frame
	ret, frame = cap.read()

	if ret == True:
		cv2.namedWindow('Thermal',cv2.WINDOW_NORMAL)
		cv2.imshow('Thermal',frame)

		keyPress = cv2.waitKey(3)
		if keyPress == ord('q'):
			break
			capture.release()
			cv2.destroyAllWindows()
