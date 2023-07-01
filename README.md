# PyThermalcam
Python Software to use the Topdon TC001 Thermal Camera on Linux and the Raspberry Pi

Huge kudos to LeoDJ on the EEVBlog forum for reverse engineering the image format from these kind of cameras (InfiRay P2 Pro) to get the raw temperature data!
https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
Check out Leo's Github here: https://github.com/LeoDJ/P2Pro-Viewer/tree/main

---

***Introduction***

This is a quick and dirty Python implimentation of Thermal Camera software for the Topdon TC001!
(https://www.amazon.co.uk/dp/B0BBRBMZ58)
No commands are sent the the camera, instead, we take the raw video feed, do some openCV magic, and display a nice heatmap along with relevant temperature points highlighted.

![Screenshot](media/TC00120230701-131032.png)

This program, and associated information is Open Source (see Licence), but if you have gotten value from these kinds of projects and think they are worth something, please consider donating: https://paypal.me/leslaboratory?locale.x=en_GB 

This readme is accompanied by youtube videos. Visit my Youtube Channel at: https://www.youtube.com/leslaboratory

---

***Features***


Tested on Debian all features are working correctly This has been tested on the Pi However a number of workarounds are implemented! Seemingly there are bugs in the compiled version of openCV that ships with the Pi!!

The following features have been implemented:

<img align="right" src="media/colormaps.png">

- Bicubic interpolation to scale the small 256*192 image to something more presentable! Available scaling multiplier range from 1-5 (Note: This will not auto change the window size on the Pi (openCV needs recompiling), however you can manually resize). Optional blur can be applied if you want to smooth out the pixels. 
- Fullscreen / Windowed mode (Note going back to windowed  from fullscreen does not seem to work on the Pi! OpenCV probably needs recompiling!).
- False coloring of the video image is provided. the avilable colormaps are listed on the right.
- Variable Contrast.
- Average Scene Temperature.
- Center of scene temperature monitoring (Crosshairs).
- Floating Maximum and Minimum temperature values within the scene, with variable threshold.
- Video recording is implemented (saved as AVI in the working directory).
- Snapshot images are implemented (saved as PNG in the working directory).

The current settings are displayed in a box at the top left of the screen (The HUD):

- Avg Temperature of the scene
- Label threshold (temperature threshold at which to display floating min max values)
- Colormap
- Blur (blur radius)
- Scaling multiplier
- Contrast value
- Time of the last snapshot image
- Recording status


---

***Key Bindings***


a z: Increase/Decrease Blur

s x: Floating High and Low Temp Label Threshold'

d c: Change Interpolated scale Note: This will not change the window size on the Pi

f v: Contrast

q w: Fullscreen Windowed (note going back to windowed does not seem to work on the Pi!)

r t: Record and Stop

m : Cycle through ColorMaps

h : Toggle HUD
