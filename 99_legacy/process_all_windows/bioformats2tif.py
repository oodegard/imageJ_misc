#@ File    (label = "Input directory", style = "directory") srcFile
#@ File    (label = "Output directory", style = "directory") dstFile
#@ String  (label = "File extension", value=".tif") ext
#@ String  (label = "File name contains", value = "") containString
#@ boolean (label = "Keep directory structure when saving", value = true) keepDirectories

# See also Process_Folder.ijm for a version of this code
# in the ImageJ 1.x macro language.

import os
from ij import IJ, ImagePlus
from loci.plugins import BF

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
  # Give a new name for image
  outName = os.path.splitext(fileName)[0]
  print(outName)
  
  # Opening the image
  print "Open image file", os.path.join(currentDir, fileName)
  #imp = IJ.openImage(os.path.join(currentDir, fileName))
  imps = BF.openImagePlus(os.path.join(currentDir, fileName))
  
  n = 0
  for imp in imps:
    #imp.show()

    # If more than one image is opened set n as name extension
    if(n > 0):
      outName = outName + "_" + n
    n = n + 1
    
    # Saving the image
    saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
    if not os.path.exists(saveDir):      
      os.makedirs(saveDir)
    
    print "Saving to", os.path.join(saveDir, outName + ".tif")
    IJ.saveAs(imp, "Tiff", os.path.join(saveDir, outName + ".tif"));
    imp.close()

      
   
  # Put your processing commands here!
   

 
run()
