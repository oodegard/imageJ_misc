# This script will process an image
#@ String (label = "Input file path") filepath
#@ File (label = "Output directory", style = "directory") dstDir

import os
from ij import IJ, ImagePlus, WindowManager
from ij.gui import OvalRoi, Roi, WaitForUserDialog
from ij.plugin.frame import RoiManager
from ij.plugin import ZProjector
from loci.plugins import BF
from ij.plugin import ChannelSplitter

def manual_add_trace(filepath, dstDir):
	print "Processing:"
	 
	# Opening the image
	print "Open image file", filepath
	print "filepath type", str(filepath)
	imps = BF.openImagePlus(str(filepath))  	
	
  	trace_count = 1
  	for imp in imps:
  		if(imp.getDimensions()[3]>1):
  			imp = ZProjector.run(imp,"max all")
  		if(imp.getDimensions()[2]>1):
  			if(showAllChannels):
  				tileChannels(imp)
  			else:
  				imp = makeRGB(imp)
  		else:
  			imp.show()
  		
		nTraces = 1
		while nTraces != 0:
			outname = os.path.join(dstDir, os.path.splitext(os.path. basename(fileName))[0] + "_" + str(trace_count) + ".zip")
			print("trace #: " + str(nTraces))
						
			# ROI manager
			IJ.run("ROI Manager...", "")
			rm = RoiManager.getInstance()
			rm.runCommand(imp,"Show None");

			if(os.path.exists(outname)):
				print("editTrace: " + outname)
				editTrace(outname, imp, rm)
			else:
				if(processtraces):
					continue
				print("getTrace: " + outname)
				getTrace()

			nTraces = rm.getCount()
			if(WindowManager.getImageCount() == 0):
				# Exit loop if image is closed
				sys.exit()
			if(nTraces != 0):
				# Save traces
				if os.path.exists(outname):
					os.remove(outname)				
				rm.runCommand(imp,"Deselect")
				rm.runCommand("Save", outname)				
				rm.runCommand(imp,"Deselect");
				rm.runCommand(imp,"Delete");
				trace_count = trace_count + 1
			else:
				if os.path.exists(outname):
					os.remove(outname)	
			print("nImages: ", WindowManager.getImageCount())
		imp.close()
		IJ.run("Close All", "");

def getTrace():
	IJ.setTool("point")
	IJ.run("Point Tool...", "type=Hybrid color=Yellow size=Small auto-next add")
	myWait = WaitForUserDialog("Select ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()
	
def editTrace(path, imp, rm):
	rm.runCommand("open", path)
	rm.select(0)
	rm.runCommand(imp,"Show All");
	myWait = WaitForUserDialog("Edit ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()

def makeRGB(imp):
	for i in range(0, imp.getDimensions()[2]):
		imp.setC(i+1)
		IJ.run(imp, "Enhance Contrast", "saturated=0.1")
	imp.setC(1)
	IJ.run(imp, "Make Composite", "")
	IJ.run(imp, "RGB Color", "frames")
	imp
	return(imp)
	
def tileChannels(imp):
	channels = ChannelSplitter.split(imp);
	imp.hide()
	for ch in channels:
		ch.show()
		IJ.run(ch, "Enhance Contrast", "saturated=0.1")
	IJ.run("Tile", "")

	
	IJ.run("Synchronize Windows", "")



# Run
showAllChannels = True

manual_add_trace(filepath, dstDir)

