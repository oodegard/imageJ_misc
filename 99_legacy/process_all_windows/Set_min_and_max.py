#@ Integer (label = "Lookup minimum", min = 0) minC
#@ Integer (label = "Lookup maximum", min = 0) maxC

import ij.IJ as IJ
from ij import WindowManager as WM
import time # tmp for tesing
 
img_titles = WM.getImageTitles();



for img_title in img_titles:
	IJ.selectWindow(img_title); # select window with img_title
	imp = IJ.getImage(); # load selected window
	imp.getProcessor().setMinAndMax(minC, maxC); # set min and max value
	imp.updateAndDraw(); # update contrast to imp
	imp.show(); # show image