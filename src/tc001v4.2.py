#!/usr/bin/env python3
"""
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!
"""

import argparse
import io
import time
import textwrap

import cv2
import numpy as np

print(textwrap.dedent("""\
	Les Wright 21 June 2023
	https://youtube.com/leslaboratory
	A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

	Tested on Debian all features are working correctly
	This will work on the Pi However a number of workarounds are implemented!
	Seemingly there are bugs in the compiled version of cv2 that ships with the Pi!

	Key Bindings:

	B b: Increase/Decrease Blur
	T t: Floating High and Low Temp Label Threshold
	S s: Change Interpolated scale Note: This will not change the window size on the Pi
	C c: Contrast
	f : Toggle fullscreen (note going back to windowed does not seem to work on the Pi!)
	r : Start/Stop recording
	p : Snapshot
	m : Cycle through ColorMaps
	h : Toggle HUD
	q : quit
	"""))


# We need to know if we are running on the Pi, because openCV behaves a little oddly on all the builds!
# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
def is_raspberrypi():
	try:
		with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
			if 'raspberry pi' in m.read().lower():
				return True
	except Exception:
		pass
	return False


isPi = is_raspberrypi()

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()

if args.device:
	dev = args.device
else:
	dev = 0

# init video
cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
#cap = cv2.VideoCapture(0)
# pull in the video but do NOT automatically convert to RGB, else it breaks the temperature data!
# https://stackoverflow.com/questions/63108721/opencv-setting-videocap-property-to-cap-prop-convert-rgb-generates-weird-boolean
try:
	cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
except TypeError:
	cap.set(cv2.CAP_PROP_CONVERT_RGB, False)

# 256x192 General settings
width = 256  # Sensor width
height = 192  # sensor height
scale = 3  # scale multiplier
newWidth = width*scale
newHeight = height*scale
alpha = 1.0  # Contrast control (1.0-3.0)
colormap = 0
FONT = cv2.FONT_HERSHEY_SIMPLEX
dispFullscreen = False
cv2.namedWindow('Thermal', cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal', newWidth, newHeight)
rad = 0  # blur radius
threshold = 2
hud = True
recording = False
elapsed = "00:00:00"
snaptime = "None"


def rec():
	now = time.strftime("%Y%m%d--%H%M%S")
	# do NOT use mp4 here, it is flakey!
	videoOut = cv2.VideoWriter(now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'), 25, (newWidth, newHeight))
	return videoOut


def snapshot(heatmap):
	# I would put colons in here, but it Win throws a fit if you try and open them!
	now = time.strftime("%Y%m%d-%H%M%S")
	snaptime = time.strftime("%H:%M:%S")
	cv2.imwrite("TC001"+now+".png", heatmap)
	return snaptime


while cap.isOpened():
	# Capture frame-by-frame
	ret, frame = cap.read()
	if ret:
		imdata, thdata = np.array_split(frame, 2)
		# now parse the data from the bottom frame and convert to temp!
		# https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
		# Huge props to LeoDJ for figuring out how the data is stored and how to compute temp from it.
		# grab data from the center pixel...
		hi = thdata[96][128][0]
		lo = thdata[96][128][1]
		#print(hi,lo)
		lo = lo*256
		rawtemp = hi+lo
		#print(rawtemp)
		temp = (rawtemp/64)-273.15
		temp = round(temp, 2)
		#print(temp)
		#break

		# find the max temperature in the frame
		lomax = thdata[..., 1].max()
		posmax = thdata[..., 1].argmax()
		# since argmax returns a linear index, convert back to row and col
		mcol, mrow = divmod(posmax, width)
		himax = thdata[mcol][mrow][0]
		lomax = lomax*256
		maxtemp = himax+lomax
		maxtemp = (maxtemp/64)-273.15
		maxtemp = round(maxtemp, 2)

		# find the lowest temperature in the frame
		lomin = thdata[..., 1].min()
		posmin = thdata[..., 1].argmin()
		# since argmax returns a linear index, convert back to row and col
		lcol, lrow = divmod(posmin, width)
		himin = thdata[lcol][lrow][0]
		lomin = lomin*256
		mintemp = himin+lomin
		mintemp = (mintemp/64)-273.15
		mintemp = round(mintemp, 2)

		# find the average temperature in the frame
		loavg = thdata[..., 1].mean()
		hiavg = thdata[..., 0].mean()
		loavg = loavg*256
		avgtemp = loavg+hiavg
		avgtemp = (avgtemp/64)-273.15
		avgtemp = round(avgtemp, 2)

		# Convert the real image to RGB
		bgr = cv2.cvtColor(imdata,  cv2.COLOR_YUV2BGR_YUYV)
		# Contrast
		bgr = cv2.convertScaleAbs(bgr, alpha=alpha)  # Contrast
		# bicubic interpolate, upscale and blur
		bgr = cv2.resize(bgr, (newWidth, newHeight), interpolation=cv2.INTER_CUBIC)  # Scale up!
		if rad > 0:
			bgr = cv2.blur(bgr, (rad, rad))

		# apply colormap
		if colormap == 0:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_JET)
			cmapText = 'Jet'
		if colormap == 1:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_HOT)
			cmapText = 'Hot'
		if colormap == 2:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_MAGMA)
			cmapText = 'Magma'
		if colormap == 3:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_INFERNO)
			cmapText = 'Inferno'
		if colormap == 4:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PLASMA)
			cmapText = 'Plasma'
		if colormap == 5:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_BONE)
			cmapText = 'Bone'
		if colormap == 6:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_SPRING)
			cmapText = 'Spring'
		if colormap == 7:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_AUTUMN)
			cmapText = 'Autumn'
		if colormap == 8:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_VIRIDIS)
			cmapText = 'Viridis'
		if colormap == 9:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PARULA)
			cmapText = 'Parula'
		if colormap == 10:
			heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_RAINBOW)
			heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
			cmapText = 'Inv Rainbow'

		#print(heatmap.shape)

		# draw crosshairs
		cv2.line(heatmap, (newWidth//2, newHeight//2+20),
				(newWidth//2, newHeight//2-20), (255, 255, 255), 2)  # vline
		cv2.line(heatmap, (newWidth//2+20, newHeight//2),
				(newWidth//2-20, newHeight//2), (255, 255, 255), 2)  # hline

		cv2.line(heatmap, (newWidth//2, newHeight//2+20),
				(newWidth//2, newHeight//2-20), (0, 0, 0), 1)  # vline
		cv2.line(heatmap, (newWidth//2+20, newHeight//2),
				(newWidth//2-20, newHeight//2), (0, 0, 0), 1)  # hline
		#show temp
		cv2.putText(heatmap, str(temp)+' C', (newWidth//2+10, newHeight//2-10),
					FONT, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
		cv2.putText(heatmap, str(temp)+' C', (newWidth//2+10, newHeight//2-10),
					FONT, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

		if hud:
			# display black box for our data
			cv2.rectangle(heatmap, (0, 0), (160, 120), (0, 0, 0), -1)
			# put text in the box
			cv2.putText(heatmap, 'Avg Temp: '+str(avgtemp)+' C', (10, 14),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			cv2.putText(heatmap, 'Label Threshold: '+str(threshold)+' C', (10, 28),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			cv2.putText(heatmap, 'Colormap: '+cmapText, (10, 42),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			cv2.putText(heatmap, 'Blur: '+str(rad)+' ', (10, 56),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			cv2.putText(heatmap, 'Scaling: '+str(scale)+' ', (10, 70),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			cv2.putText(heatmap, 'Contrast: '+str(alpha)+' ', (10, 84),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			cv2.putText(heatmap, 'Snapshot: '+snaptime+' ', (10, 98),
						FONT, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

			if not recording:
				cv2.putText(heatmap, 'Recording: '+elapsed, (10, 112),
							FONT, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
			else:
				cv2.putText(heatmap, 'Recording: '+elapsed, (10, 112),
							FONT, 0.4, (40, 40, 255), 1, cv2.LINE_AA)

		# Yeah, this looks like we can probably do this next bit more efficiently!
		# display floating max temp
		if maxtemp > avgtemp+threshold:
			cv2.circle(heatmap, (mrow*scale, mcol*scale), 5, (0, 0, 0), 2)
			cv2.circle(heatmap, (mrow*scale, mcol*scale), 5, (0, 0, 255), -1)
			cv2.putText(heatmap, str(maxtemp)+' C', ((mrow*scale)+10, (mcol*scale)+5),
						FONT, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
			cv2.putText(heatmap, str(maxtemp)+' C', ((mrow*scale)+10, (mcol*scale)+5),
						FONT, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

		# display floating min temp
		if mintemp < avgtemp-threshold:
			cv2.circle(heatmap, (lrow*scale, lcol*scale), 5, (0, 0, 0), 2)
			cv2.circle(heatmap, (lrow*scale, lcol*scale), 5, (255, 0, 0), -1)
			cv2.putText(heatmap, str(mintemp)+' C', ((lrow*scale)+10, (lcol*scale)+5),
						FONT, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
			cv2.putText(heatmap, str(mintemp)+' C', ((lrow*scale)+10, (lcol*scale)+5),
						FONT, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

		# display image
		cv2.imshow('Thermal', heatmap)

		if recording:
			elapsed = (time.time() - start)
			elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed))
			#print(elapsed)
			videoOut.write(heatmap)

		keyPress = cv2.waitKey(1)
		if not (ord("A") <= keyPress <= ord("z")):
			continue
		if keyPress == 'B':  # Increase blur radius
			rad += 1
		if keyPress == 'b':  # Decrease blur radius
			rad -= 1
			if rad <= 0:
				rad = 0

		if keyPress == 'T':  # Increase threshold
			threshold += 1
		if keyPress == 't':  # Decrease threshold
			threshold -= 1
			if threshold <= 0:
				threshold = 0

		if keyPress == 'S':  # Increase scale
			scale += 1
			if scale >= 5:
				scale = 5
			newWidth = width*scale
			newHeight = height*scale
			if not dispFullscreen and not isPi:
				cv2.resizeWindow('Thermal', newWidth, newHeight)
		if keyPress == 's':  # Decrease scale
			scale -= 1
			if scale <= 1:
				scale = 1
			newWidth = width*scale
			newHeight = height*scale
			if not dispFullscreen and not isPi:
				cv2.resizeWindow('Thermal', newWidth, newHeight)

		if keyPress == 'f':  # toggle fullscreen
			if not dispFullscreen:
				dispFullscreen = True
				cv2.namedWindow('Thermal', cv2.WND_PROP_FULLSCREEN)
				cv2.setWindowProperty('Thermal', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
			else:
				dispFullscreen = False
				cv2.namedWindow('Thermal', cv2.WINDOW_GUI_NORMAL)
				cv2.setWindowProperty('Thermal', cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_GUI_NORMAL)
				cv2.resizeWindow('Thermal', newWidth, newHeight)

		if keyPress == 'C':  # contrast+
			alpha += 0.1
			alpha = round(alpha, 1)  # fix round error
			if alpha >= 3.0:
				alpha = 3.0
		if keyPress == 'c':  # contrast-
			alpha -= 0.1
			alpha = round(alpha, 1)  # fix round error
			if alpha <= 0:
				alpha = 0.0

		if keyPress == 'h':
			hud = not hud

		if keyPress == 'm':  # m to cycle through color maps
			colormap += 1
			if colormap == 11:
				colormap = 0

		if keyPress == 'r':
			if not recording:  # start recording
				videoOut = rec()
				start = time.time()
			else:  # finish recording
				elapsed = "00:00:00"
			recording = not recording

		if keyPress == 'p':  # take a snapshot
			snaptime = snapshot(heatmap)

		if keyPress == 'q':
			break
			capture.release()
			cv2.destroyAllWindows()
