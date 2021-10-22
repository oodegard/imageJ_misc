#@ String(visibility="MESSAGE", value="Select folder and pattern") text1
#@ File    (label = "Input directory", style = "directory") srcFile
#@ File    (label = "Output directory", style = "directory") dstFile
#@ String  (label = "File extension", value=".tif") ext
#@ String  (label = "File name contains", value = "") containString
## boolean (label = "Keep directory structure when saving", value = true) keepDirectories
#@ String(visibility="MESSAGE", value="Temporal color code settings") text2
#@ String (label="Select LUT", choices={"Fire", "Fire_inv", "mpl-viridis", "Rainbow RGB"}, value="Fire") glut
#@ Integer (label="Start frame", value=1, min=1 ) gstartf_f
#@ Integer (label="End frame (-1 means all frames)", value=-1, min=-1) gendf_f
#@ Integer (label="Create Time Color Scale Bar", min = 0, max = 1) gframecolorscale_f

# See also Process_Folder.ijm for a version of this code
# in the ImageJ 1.x macro language.

print(glut_f)

import os
from ij import IJ, ImagePlus, WindowManager
from loci.plugins import BF

# Setup
IJ.run("Close All", "")
keepDirectories = False


def run():

  srcDir = srcFile.getAbsolutePath()
  dstDir = dstFile.getAbsolutePath()
  for root, directories, filenames in os.walk(srcDir):
    filenames.sort();
    for filename in filenames:
      # Check for file extension
      if not filename.endswith(ext):
        continue
      # Check for file name pattern
      if containString not in filename:
        continue
      process(srcDir, dstDir, root, filename, keepDirectories)
 
def process(srcDir, dstDir, currentDir, fileName, keepDirectories):
  print "Processing:"
   
  # Opening the image
  print ("Open image file: " + os.path.join(currentDir, fileName))
  
  #imp = IJ.openImage(os.path.join(currentDir, fileName))
  #IJ.run("Bio-Formats Importer", "open=D:/01_Image_Data/20210225_#17/1-RPE-1_Phafin2-GFP_3sec_001_visit_1_ALX_D3D.dv color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack");

  imps = BF.openImagePlus(os.path.join(currentDir, fileName))
  for imp in imps:
    imp.show()
    # Put your processing commands here!
    IJ.run("temporal color code process multichannel", "glut_mc=[" + str(glut_f) + "], gstartf_mc=[" + str(gstartf_f) + "], gendf_mc=[" + str(gendf_f) + "], gframecolorscale_mc=[" + str(gframecolorscale_f) + "]") # Will run headless
    imp.close()
	
    # Saving the image
    saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
    if not os.path.exists(saveDir):
      os.makedirs(saveDir)
    print "Saving to", saveDir
  
    IJ.selectWindow("temporal_merge")
    imp = IJ.getImage()  	
    IJ.saveAs(imp, "Tiff", os.path.join(saveDir, os.path.splitext(fileName)[0] + "_temporal_merge.tif"))
    imp.close()
  
    #IJ.selectWindow("color time scale")
    imp = IJ.getImage()  	
    IJ.saveAs(imp, "Tiff", os.path.join(saveDir, os.path.splitext(fileName)[0] + "_temporal_merge_scale.tif"))
    imp.close()
  
    # Save all other opened images with the image title as name
    for imp in map(WindowManager.getImage, WindowManager.getIDList()):
      IJ.run(imp, "AVI... ", "compression=JPEG frame=10 save=[" + os.path.join(saveDir, os.path.splitext(fileName)[0]) + imp.getTitle() + ".avi" +"]")
    IJ.run("Close All", "")
    
run()
