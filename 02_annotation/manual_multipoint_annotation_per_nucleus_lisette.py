from ij import IJ, ImagePlus, WindowManager
from ij.plugin import ZProjector, Duplicator
from ij.gui import OvalRoi, Roi, WaitForUserDialog, PointRoi
from ij.plugin.frame import RoiManager
from loci.plugins import BF
import os
import sys
import shutil
#from ijmisc_oof import get1DMaxima
import glob
from ij.measure import ResultsTable
from ij.text import TextWindow
	

#@ File    (label = "Input directory", style = "directory") srcfile
## File    (label = "Output directory", style = "directory") dstfile
#@ String  (label = "File extension", value=".tif") ext
#@ String  (label = "File name contains", value = "") containstring
#@ String  (label = "File name not contains", value = "") notcontainstring
#@ Boolean (label = "Skip image if annotated") skipannotated
#@ Integer (label = "Nucleus channel", min=1, value=1) nuc_ch


## If the folder structure of your input directory should be kept
keepDirectories = False

## Lists all files in folder
## Runs files with correct extension and containstring
def run(output_folder_ext, nuc_seg_ext, nucleus_annotation_ext):
	srcDir = srcfile.getAbsolutePath()
	#dstDir = dstfile.getAbsolutePath()
	dstDir = srcDir + output_folder_ext
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
	
	makeResultsTable(dstDir)

# This function will open one image and call manual_annotate_4D or editTrace as long as there are ROIs in the ROI manager
# The function will save each ROI output_dir with the same file name + track ID + .zip  
def processImage(image_path, output_dir):
	print("Run analysis: " + image_path)
	# Define output name
	outNameBase = os.path.splitext(os.path.basename(str(image_path)))[0]

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

		segmentation_file_name = os.path.join(output_dir, outNameBase + nuc_seg_ext + ".zip")
		
		if(not os.path.exists(segmentation_file_name)):
			# Fin all nuclei
			nuc = Duplicator().run(imp, nuc_ch, nuc_ch, 1, 1, 1, 1)
			IJ.run(nuc, "Convert to Mask", "Intermodes dark")
	
			# Delete all ROIs in ROI manager
			if(rm.getCount()>0):
				rm.runCommand(imp,"Deselect")
				rm.runCommand(imp,"Delete")
			
			# Find nuclei and add to manager
			IJ.run(nuc, "Analyze Particles...", "size=100-Infinity exclude clear add");

			# Save nucleus segmentation
			rm.runCommand(imp,"Deselect");
			rm.save(segmentation_file_name);

		else:
			rm.open(segmentation_file_name)
		
		imp.setDisplayMode(IJ.COMPOSITE);
		imp.show() # To activate composite img
		imp.hide()

		if(rm.getCount()>0):
			for i, r in enumerate(rm): # For each nucleus	
				imp_flat = imp.flatten()
				imp_flat.show()
				rm.select(i)
				imp_flat2 = imp_flat.flatten()
				imp_flat.close()
				imp_flat2
		
				# Delete all ROIs in ROI manager
				if(rm.getCount()>0):
					rm.runCommand(imp,"Deselect")
					rm.runCommand(imp,"Delete")
				
				# Let the user define new trace, or open existing trace 
				outName = os.path.join(output_dir, outNameBase + nucleus_annotation_ext + str(i) + ".zip")	 
				if(not os.path.exists(outName)):			
					rm = manual_annotate_4D(imp_flat2, rm, "") # manual annotate new position
				elif(not skipannotated):
					rm = manual_annotate_4D(imp_flat2, rm, outName) # Open and edit existing annotation
				else:
					continue
					

				imp_flat2.close()
				
				
				# If the file exist from before delete it before saving it again based on edits from user
				if os.path.exists(outName):
					os.remove(outName)
				
				# Save
				if(rm.getCount()>0):
					rm.runCommand(imp,"Deselect");
					rm.save(outName);

				# Delete all ROIs in ROI manager
				if(rm.getCount()>0):
					rm.runCommand(imp,"Deselect")
					rm.runCommand(imp,"Delete")
				
				rm.open(segmentation_file_name);
		if(rm.getCount()>0):
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
	rm.runCommand(imp,"Show All");
	myWait = WaitForUserDialog("Select ROIs", "Select one or more ROIs covering each feature to track")
	myWait.show()
	
	# Exit program if image is closed
	if(WindowManager.getImageCount() == 0):
		sys.exit()
	else:
		imp.hide()
		
	# return ROI Manager
	return rm

def makeResultsTable(dstDir):
	# Read all nucleus segmentation files
	ext_search = dstDir + "\\*" + nuc_seg_ext + "*.zip"
	
	rm = RoiManager.getInstance()
	rm.close()
	IJ.run("ROI Manager...", "") # open a empty ROI manager
	if(rm.getCount()>0):
		rm.runCommand(imp,"Deselect");
		rm.runCommand(imp,"Delete");
	
	# Make results table
	rt_exist = WindowManager.getWindow("Results table")
	if rt_exist==None or not isinstance(rt_exist, TextWindow):
	    rt= ResultsTable()
	else:
	    rt = rt_exist.getTextPanel().getOrCreateResultsTable()
	rt_counter = 0
	
	for f in glob.glob(ext_search):
		IJ.run("ROI Manager...", "") # open a empty ROI manager
		rm = RoiManager.getInstance()
		rm.open(f)
		nNuclei = rm.getCount() # used to count cells with zero points in
		rm.close() # close roi manager so that it can be used for annotations

		
		nuc_ids = range(nNuclei) # search for zip filea with these IDs
		for nucid in nuc_ids:
			annotation_file_name = os.path.splitext(os.path.basename(str(f)))[0]
			annotation_file_name_search =  dstDir + "\\" + annotation_file_name.replace(nuc_seg_ext, nucleus_annotation_ext) + str(nucid) + ".zip"		

			rt.setValue("file_name", rt_counter, annotation_file_name);
			rt.setValue("nucleus_id", rt_counter, nucid);			
			
			
			if(os.path.exists(annotation_file_name_search)):
				IJ.run("ROI Manager...", "") # open a empty ROI manager
				rm = RoiManager.getInstance()
				rm.open(annotation_file_name_search)							
				
				rt.setValue("annotation_count", rt_counter, rm.getCount());
				rt.show("Results table")
				rm.close()
			else:
				rt.setValue("annotation_count", rt_counter, 0); # Add zero cell if no zip file
			
			rt_counter = rt_counter + 1 
			
	# Save results table
	rt.saveAs(dstDir + "\\" + "Results_annotations" + ".tsv")

		
# Run
IJ.run("required imageJ version", "version=1.53k") # Auto-next slice was updated in 1.53k

# input
output_folder_ext = "_annotation"
nuc_seg_ext = "_nuc_seg"
nucleus_annotation_ext = "_nucleus_annotation_"

# Run
IJ.run("Close All", "")
IJ.run("ROI Manager...", "") # Needs to be open before use
run(output_folder_ext, nuc_seg_ext, nucleus_annotation_ext)

IJ.run("Close All", "")


# Make results table

