# PyThermalcam
Python Software to use the Topdon TC001 Thermal Camera on Linux and the Raspberry Pi

Huge kudos to LeoDJ on the EEVBlog forum for reverse engineering the image format from these kind of cameras (InfiRay P2 Pro)!
https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
Chek out Leo's Github here: https://github.com/LeoDJ/P2Pro-Viewer/tree/main


This is a quick and dirty Python implimentation of Thermal Camera software for the Topdon TC001!
(https://www.amazon.co.uk/dp/B0BBRBMZ58)
No commands are sent the the camera, instead, we take the raw video feed, do some openCV magic, and display a nice heatmap along with relevant temperature points highlighted.


This program, and associated information is Open Source (see Licence), but if you have gotten value from these kinds of projects and think they are worth something, please consider donating: https://paypal.me/leslaboratory?locale.x=en_GB This project is a follow on from: https://github.com/leswright1977/PySpectrometer

This readme is accompanied by youtube videos. Visit my Youtube Channel at: https://www.youtube.com/leslaboratory
