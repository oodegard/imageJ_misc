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


def find_nuclei(nuc):
	rm = RoiManager.getRoiManager() # New ROI manager
	
	IJ.setAutoThreshold(nuc, "MaxEntropy dark");
	IJ.run(nuc, "Convert to Mask", "MaxEntropy dark")
	IJ.run(nuc, "Fill Holes", "");
			
	# Delete all ROIs in ROI manager
	if(rm.getCount()>0):
		rm.runCommand(imp,"Deselect")
		rm.runCommand(imp,"Delete")
						
	# Find nuclei and add to manager
	IJ.run(nuc, "Analyze Particles...", "size=" + str(minCellSize) + "-Infinity pixel exclude clear add");
	#IJ.run(nuc, "Analyze Particles...", "size=" + minCellSize + "-Infinity exclude clear add");


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
		IJ.run("ROI Manager...", "") # open a empty ROI manager
		rm = RoiManager.getInstance()
		if(rm.getCount()>0):
			rm.runCommand(imp,"Deselect");
			rm.runCommand(imp,"Delete");

		# Max project if  number of z dimension > 1
		if(imp.getDimensions()[3]>1):
  			imp = ZProjector.run(imp,"max all")

		#segmentation_file_name = os.path.join(output_dir, outNameBase + nuc_seg_ext + ".zip")
		roi_zip_name = os.path.join(output_dir, outNameBase + nuc_seg_ext + ".zip")
		roi_roi_name = os.path.join(output_dir, outNameBase + nuc_seg_ext + ".roi")
		roi_txt_name = os.path.join(output_dir, outNameBase + nuc_seg_ext + ".txt")

		if(os.path.exists(roi_zip_name)):
			roi_path = roi_zip_name
		elif(os.path.exists(roi_roi_name)):
			roi_path = roi_roi_name
		else:
			roi_path = False
		print(roi_path)
		
		if(roi_path == False): # Make a new segmentation
			# Fin all nuclei		
			nuc = Duplicator().run(imp, nuc_ch, nuc_ch, 1, 1, 1, 1)
			find_nuclei(nuc)
			
			# Add edit nuc segmentation
			# code placeholder

			# Save nucleus segmentation
			rm = RoiManager.getInstance()
			
			if(rm.getCount()>1):
				rm.runCommand(nuc,"Deselect");
				rm.save(roi_zip_name);
			elif(rm.getCount()==1): # somehow I can not save a single roi in a zip folder
				rm.select(0)
				rm.save(roi_roi_name)
			else: # save a txt file if no nucleus found
				IJ.saveString("No nucleus found", roi_txt_name)	
		else:		
			rm.open(roi_path)
		
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
					annotation_zip_name = os.path.join(output_dir, outNameBase + nucleus_annotation_ext + str(i) + ".zip")
					annotation_roi_name = os.path.join(output_dir, outNameBase + nucleus_annotation_ext + str(i) + ".roi")
					annotation_txt_name = os.path.join(output_dir, outNameBase + nucleus_annotation_ext + str(i) + ".txt")
	
					# check if any roi file exist from before
					if(os.path.exists(annotation_zip_name)):
						annotation_name = annotation_zip_name
					elif(os.path.exists(annotation_roi_name)):
						annotation_name = annotation_roi_name
					else:
						annotation_name = False
	
					rm = RoiManager.getInstance()	
					
					if(annotation_name != False):
						rm.open(annotation_name)
					
					# Manual annotation of cells
					if(any([not skipannotated , annotation_name == False])):
						rm = manual_annotate_4D(imp_flat2, rm)

					
					# If the file exist from before delete it before saving it again based on edits from user
					if os.path.exists(annotation_zip_name):
						os.remove(annotation_zip_name)
					if os.path.exists(annotation_roi_name):
						os.remove(annotation_roi_name)
					if os.path.exists(annotation_txt_name):
						os.remove(annotation_txt_name)	
								
					# Save
					if(rm.getCount()>1):
						rm.runCommand(imp_flat2,"Deselect");
						rm.save(annotation_zip_name);
					elif(rm.getCount()==1): # somehow I can not save a single roi in a zip folder
						rm.select(0)
						rm.save(annotation_roi_name)
					else: # save a txt file if no nucleus found
						IJ.saveString("No nucleus found", annotation_txt_name)	
					
					# Delete all ROIs in ROI manager
					rm = RoiManager.getInstance()
					if(rm.getCount()>0):
						rm.runCommand(imp_flat2,"Deselect")
						rm.runCommand(imp_flat2,"Delete")
					
				imp_flat2.close()
				rm.open(roi_path); # re open the nuclear segmentation ROI
		

def manual_annotate_4D(imp, rm):

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
	ext_search_zip = glob.glob(dstDir + "\\*" + nuc_seg_ext + "*.zip")
	ext_search_roi = glob.glob(dstDir + "\\*" + nuc_seg_ext + "*.roi")
	ext_search = ext_search_zip + ext_search_roi
	
	rm = RoiManager.getInstance()
	rm.close()
			
	# Make results table
	rt_exist = WindowManager.getWindow("Results table")
	if rt_exist==None or not isinstance(rt_exist, TextWindow):
	    rt= ResultsTable()
	else:
	    rt = rt_exist.getTextPanel().getOrCreateResultsTable()
	rt_counter = 0

	
	for f in ext_search:
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
minCellSize = 10


# Run
IJ.run("Close All", "")

run(output_folder_ext, nuc_seg_ext, nucleus_annotation_ext)

IJ.run("Close All", "")


# Make results table

