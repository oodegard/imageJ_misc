from ij import IJ, ImagePlus, WindowManager
from ij.plugin import ZProjector, Duplicator
from ij.gui import OvalRoi, Roi, WaitForUserDialog, PointRoi
from ij.plugin.frame import RoiManager
from loci.plugins import BF
import os
import sys
import shutil

#@ File    (label = "Input directory", style = "directory") srcfile
## File    (label = "Output directory", style = "directory") dstfile
#@ String  (label = "File extension", value=".tif") ext
#@ String  (label = "File name contains", value = "") containstring
keepDirectories = False

global ch_default
ch_default = 1 # Will only desice which ch to start in 

## Lists all files in folder
## Runs files with correct extension and containstring

def run():
	srcDir = srcfile.getAbsolutePath()
	#dstDir = dstfile.getAbsolutePath()
	dstDir = srcDir + "_traces2"
	
	if srcDir == dstDir:
		sys.exit("srcDir == dstDir is not allowed")
	if not os.path.exists(dstDir):
		os.mkdir(dstDir)	
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort();
	for filename in filenames:
		# Check for file extension
		if not filename.endswith(ext):
			continue
		# Check for file name pattern
		if containstring not in filename:
			continue
		# Process image
		processImage(os.path.join(srcDir, filename), dstDir)

# This function will open one image and call manual_annotate_4D or editTrace as long as there are ROIs in the ROI manager
# The function will save each ROI output_dir with the same file name + track ID + .zip  
def processImage(image_path, output_dir):
	# Define output name
	outNameBase = os.path.splitext(os.path.basename(str(image_path)))[0]
	print outNameBase
		
	# Open image
	imps = BF.openImagePlus(str(image_path))
	
	counter = 0
	for imp in imps:
		IJ.run(imp, "Enhance Contrast", "saturated=0.01")
		# Make/empty ROI manager
		rm = RoiManager.getInstance()
		if(rm.getCount()>0):
			rm.runCommand(imp,"Deselect");
			rm.runCommand(imp,"Delete");

		# Max project if >1 z dimension
		if(imp.getDimensions()[3]>1):
			imp.hide()
  			imp = ZProjector.run(imp,"max all")
		
		# Reorder t and c channel if more than one c channel
		reorderTC = False
		if(imp.getDimensions()[2]>1):
			reorderTC = True
			imp.show()
			IJ.run("Re-order Hyperstack ...", "channels=[Frames (t)] slices=[Slices (z)] frames=[Channels (c)]")
			imp = IJ.getImage()
			imp.setDisplayMode(IJ.GRAYSCALE)
			imp.hide()
		
		nTraces = 1
		while (nTraces != 0):
			outName = os.path.join(output_dir, outNameBase + "_" + str(counter) + ".zip")
			outName_tpm = os.path.join(output_dir, outNameBase + "_" + str(counter) + "_tmp.zip")
			outName_oval = os.path.join(output_dir, outNameBase + "_" + str(counter) + "_oval.zip")
			print(outName)

			if(rm.getCount()>0):
				rm.runCommand(imp,"Deselect")
				rm.runCommand(imp,"Delete")
			
		
			counter = counter + 1
			 
			if(not os.path.exists(outName)):			
				rm = manual_annotate_4D(imp) # Annotate new position
			else:
				rm = editTrace(outName_tpm, imp) # Open and edit existing annotation
						
			rm = RoiManager.getInstance()
			
			if os.path.exists(outName):
				os.remove(outName)
			if os.path.exists(outName_tpm):
				os.remove(outName_tpm)
			if os.path.exists(outName_oval):
				os.remove(outName_oval)
				#shutil.rmtree(outName)
			
			nTraces = rm.getCount()
			if(nTraces>0):
			
				rm.runCommand("Save", outName_tpm) # Save
				
				# Change T and C dimension back, and add ROIs correctly to image
				if(reorderTC):
					fixSwappedCTdimension(imp)

				rm.runCommand("Save", outName) # Save
												
				# Oval around each point
				IJ.run(imp, "Select None", "")
				IJ.run("Find oval around point", "line_radius=15");

				rm.runCommand("Save", outName_oval) # Save
				
				rm.runCommand(imp,"Deselect")
				rm.runCommand(imp,"Delete")

				# Make sure they go away
				rm.runCommand(imp,"Show All");
				rm.runCommand(imp,"Show None");
				rm.runCommand(imp,"Show All");
				rm.runCommand(imp,"Show None");


					

def manual_annotate_4D(imp):	
	
	# Clear ROI manager and selections
	rm = RoiManager.getInstance()
	if(rm.getCount() >0):
		rm.runCommand(imp,"Delete")

	
	# Manual annotattion
	getTrace(imp, rm)
	
	# Exit program if image is closed
	if(WindowManager.getImageCount() == 0):
		sys.exit()
	else:
		imp.hide()
	
	# Skip to next image if roi manager is empty
	if(rm.getCount() ==0):
		IJ.run("Close All", "")
		return
		
	return rm

	
def getTrace(imp, rm):
	imp.show()
	
	IJ.setTool("point")
	IJ.run("Point Tool...", "type=Hybrid color=Yellow size=Small auto-next add")
	myWait = WaitForUserDialog("Select ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()
	

def editTrace(path, imp):
	rm = RoiManager.getInstance()
	rm.runCommand("open", path)
	rm.select(0)
	imp.show()
	imp.setC(ch_default)
	rm.runCommand(imp,"Show All");
	myWait = WaitForUserDialog("Edit ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()
	
	# Exit program if image is closed
	if(WindowManager.getImageCount() == 0):
		sys.exit()	
	return rm


def fixSwappedCTdimension(imp):
	rm = RoiManager.getInstance()
	rm.runCommand(imp,"Deselect")
	
	# Save coordinates in results table
	roi_coord = []
	for r in rm:
		p = r.getPolygon()
		x = p.xpoints[0]
		y = p.ypoints[0]
		z = r.ZPosition
		c = r.TPosition # Fix swapped dimensions
		t = r.CPosition # Fix swapped dimensions

		roi_coord.append([x,y,z,c,t])

	# Delete ROIs
	# rm.runCommand(imp,"Deselect");
	# rm.runCommand(imp,"Delete");
	
	# Change dimensions of image back to normal
	imp.show()
	IJ.run("Re-order Hyperstack ...", "channels=[Frames (t)] slices=[Slices (z)] frames=[Channels (c)]")
	imp = IJ.getImage()

	# Add Rois in correct order
	for i, r in enumerate(roi_coord):
		rm.select(i)
		imp.setZ(int(r[2]))
		#print "z", r[2]
		imp.setC(int(r[3]))
		#print "c", r[3]
		imp.setT(int(r[4]))
		#print "t", r[4]
		point = PointRoi(r[0], r[1])		
		imp.setRoi(point)
		rm.runCommand(imp,"Update")

	
	# Change dimensions of image back to inverted
	imp.show()
	IJ.run("Re-order Hyperstack ...", "channels=[Frames (t)] slices=[Slices (z)] frames=[Channels (c)]")
	imp = IJ.getImage()
	imp.setDisplayMode(IJ.GRAYSCALE)
	
	
# Run
IJ.run("Close All", "")
IJ.run("ROI Manager...", "")
run()