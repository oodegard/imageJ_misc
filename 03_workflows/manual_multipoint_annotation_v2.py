from ij import IJ, ImagePlus, WindowManager
from ij.plugin import ZProjector, Duplicator
from ij.gui import OvalRoi, Roi, WaitForUserDialog, PointRoi
from ij.plugin.frame import RoiManager
from loci.plugins import BF
import os
import sys
import shutil
from ijmisc_oof import get1DMaxima


#@ File    (label = "Input directory", style = "directory") srcfile
## File    (label = "Output directory", style = "directory") dstfile
#@ String  (label = "File extension", value=".tif") ext
#@ String  (label = "File name contains", value = "") containstring
#@ String  (label = "File name not contains", value = "") notcontainstring
#@ Boolean (label = "Skip image if annotated") skipannotated

## If the folder structure of your input directory should be kept
keepDirectories = False

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
		if notcontainstring in filename and notcontainstring != "":
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
	
	img_counter = 1 # If there are more than one image per file e.g. multipple positions
	for imp in imps:
		IJ.run(imp, "Enhance Contrast", "saturated=0.01")
		IJ.run(imp, "8-bit", "")
		
		
		# Make/empty ROI manager
		rm = RoiManager.getInstance()
		if(rm.getCount()>0):
			rm.runCommand(imp,"Deselect");
			rm.runCommand(imp,"Delete");

		# Max project if  number of z dimension > 1
		if(imp.getDimensions()[3]>1):
  			imp = ZProjector.run(imp,"max all")
		
		nROIs = 1
		trace_counter = 0 # Increases when a new trace is added to one image
		while (nROIs != 0):
			trace_counter = trace_counter + 1 
			# Set output filename for each imp in imps only if more than 1 imps
			if(len(imps)>1):
				outName = os.path.join(output_dir, outNameBase + "_i" + str(img_counter) + "_" + str(trace_counter) + ".zip")
				outName_oval = os.path.join(output_dir, outNameBase + "_i" + str(img_counter) + "_" + str(trace_counter) + "_oval.zip")
			else:
				outName = os.path.join(output_dir, outNameBase + "_" + str(trace_counter) + ".zip")
				outName_oval = os.path.join(output_dir, outNameBase + "_" + str(img_counter) + "_" + str(trace_counter) + "_oval.zip")
			print outName
			
			# Delete all ROIs in ROI manager
			if(rm.getCount()>0):
				rm.runCommand(imp,"Deselect")
				rm.runCommand(imp,"Delete")
	
			# Let the user define new trace, or open existing trace 
			
			if(not os.path.exists(outName)):			
				rm = manual_annotate_4D(imp, rm, "") # manual annotate new position
			elif(not skipannotated):
				rm = manual_annotate_4D(imp, rm, outName) # Open and edit existing annotation
			else:
				continue
						
			# If the file exist from before delete it before saving it again based on edits from user
			if os.path.exists(outName):
				os.remove(outName)
			if os.path.exists(outName_oval):
				os.remove(outName_oval)

			# Save if nROIs > 0
			nROIs = rm.getCount()
			if(nROIs>0):
				rm.runCommand("Save", outName) # Save
												
				# Compute oval around each point
				IJ.run(imp, "Select None", "")
				
				#IJ.run(imp, "Find oval around point", "line_radius=15");
				rm_oval = findOvalAroundPoints(imp, rm, 15)

				# Delete region inside rm_oval to show which slices have been selected
				IJ.setBackgroundColor(255, 255, 255); # 

				for i, r in enumerate(rm_oval):
					rm_oval.select(i)
					IJ.run(imp, "Clear", "slice");
					imp.show()
				
				IJ.setBackgroundColor(0, 0, 0); # Set back to default
				
				rm.runCommand("Save", outName_oval) # Save
				
				# Delete and hide all traces
				rm.runCommand(imp,"Deselect")
				rm.runCommand(imp,"Delete")

def manual_annotate_4D(imp, rm, path):	
	
	if(rm.getCount() >0):
		rm.runCommand(imp,"Delete")

	# Open ROI from file
	if(path != ""):
		rm.runCommand("open", path)
		rm.select(0)
	IJ.run(imp, "Select None", "");
	
	# ROI manager setup
	IJ.setTool("point")
	IJ.run("Point Tool...", "type=Hybrid color=Yellow size=Small auto-next add")
	rm.runCommand("Associate", "true")
	rm.runCommand("Centered", "false")
	rm.runCommand("UseNames", "false")

	# Open image and show OKbutton
	imp.show()
	myWait = WaitForUserDialog("Select ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()
	
	# Exit program if image is closed
	if(WindowManager.getImageCount() == 0):
		sys.exit()
	else:
		imp.hide()
		
	# return ROI Manager
	return rm

# Makes a line profile in x an y direction from a point
# Splits these two lines into four equal length segments and finds the maxima that is nearest the centre
# Adds a oval ROI that best matches these points
def findOvalAroundPoints(imp, rm, line_radius):
	print rm
	
	imp.show() # Image needs to be shown so that the selection will arrive at the correct channel and z-slice
	for i, r in enumerate(rm):
		print r, i
		rm.select(i)
		p = r.getPolygon()
		x = p.xpoints[0]
		y = p.ypoints[0]
		# z = r.ZPosition
		# c = r.TPosition # Fix swapped dimensions
		
		maxima_coords = getAllMaxima(imp, x, y, line_radius)
		print maxima_coords
		
		toOvalRoi(imp, x, y, maxima_coords, line_radius)	
		rm.runCommand(imp, "Update");
	imp.hide()
	return rm

# Returns a list with maxima coordinates and values
def getAllMaxima(imp, x, y, line_radius):
	x_values_left =   [imp.getPixel(x, y_)[0] for y_ in range(y-line_radius+1, y+1, 1) ]
	x_values_left = [v for v in reversed(x_values_left)]
	x_values_right =  [imp.getPixel(x, y_)[0] for y_ in range(y+2, y+line_radius+2, 1) ]	
	
	y_values_left =   [imp.getPixel(x_, y)[0] for x_ in range(x-line_radius+1, x+1, 1) ]
	y_values_left = [v for v in reversed(y_values_left)]
	y_values_right =  [imp.getPixel(x_, y)[0] for x_ in range(x+2, x+line_radius+2, 1) ]

	x_left = get1DMaxima(x_values_left, 0.9, line_radius)
	x_right = get1DMaxima(x_values_right, 0.9, line_radius)
	y_left = get1DMaxima(y_values_left, 0.9, line_radius)
	y_right = get1DMaxima(y_values_right, 0.9, line_radius)

	return [[[line_radius - x_left[0] + 1, line_radius + 1 + x_right[0] + 2 ], [x_left[1], x_right[1]]],[[line_radius - y_left[0] + 1, line_radius + 1 + y_right[0] +2], [y_left[1], y_right[1]]]]

# Searches for the highest value in the list from the left
# When values are decreasing and value is above threshold (e.g. 90% of max) the maxima is locked
def del_getMaxima(array, threshold, line_radius):
	print(array)
	local_max = 0
	previous_rel_intensity = 0
	for i, value in enumerate(array):
		if(value > local_max): # find local maximum
			local_max = value
			#print "new max"
		
		rel_intensity = float(value-min(array))/float(max(array) - min(array))
		# If maximum value is reached
		if(rel_intensity == 1):
			return [i, array[i]]
		
		# Stop seaching when value goes down, and previous value was above threshold
		if(value < array[max(i-1, 0)] and previous_rel_intensity > threshold):
			#print "value goes down, and previous value was above threshold"
			return [i - 1, array[i-1]]
		previous_rel_intensity = rel_intensity
	return [i, value]

def toOvalRoi(imp, x, y, coords, line_radius):
	new_x = ((x - line_radius + coords[1][0][0]) + (x - line_radius + coords[1][0][1]))/2
	new_y = ((y - line_radius + coords[0][0][0]) + (y - line_radius + coords[0][0][1]))/2
	x_rad = float(max(coords[1][0]) - min(coords[1][0]))/2
	y_rad = float(max(coords[0][0]) - min(coords[0][0]))/2
	imp.setRoi(OvalRoi(new_x  - x_rad, new_y - y_rad , x_rad*2 , y_rad*2))
	#print new_x


			
# Run
IJ.run("required imageJ version", "version=1.53k") # Auto-next slice was updated in 1.53k
IJ.run("Close All", "");
IJ.run("ROI Manager...", "") # Needs to be open before use
run()