# Create new ROI programmatically
from ij import IJ
from ij.gui import OvalRoi, Roi, WaitForUserDialog
from ij.plugin.frame import RoiManager
# Get current ImagePlus

imp = IJ.getImage()
title = imp.getTitle()
print(title)

nFrames = imp.getNFrames()

def selectROIs():
	IJ.setTool("rectangle")
	IJ.run("ROI Manager...", "")
	rm.runCommand("Associate", "true");
	myWait = WaitForUserDialog("Select ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()


# Loop over ROIs
rm = RoiManager().getInstance()
nROIs = rm.getCount()
for roi in range(nROIs):
	
	# Select ROI i
	print "ROI# = ", str(roi)
	rm.runCommand('Deselect')
	rm.select(roi)
	cur_frame = imp.getFrame()

	# Make template
	#template = imp.crop()
	#template.setTitle("template")
	#template.show()
		
	# Find next frame
	if(cur_frame + 1 <= nFrames):
		
		# Change to next frame
		imp.setT(cur_frame +1)
		rm.runCommand('Deselect')
		IJ.run(imp, "Select None", "")
		imp.show()
		myWait = WaitForUserDialog("Paise", "Select one")
		myWait.show()
		
		# Find next object
		IJ.run(imp, "cvMatch_Template...", "image=drinking_example_100ul.tif method=[Normalized cross correlation] template=template output tolerence=0.03 threshold=0");
		


		

	
	# Extract tmp template


	# Find object in next frame
	
	





