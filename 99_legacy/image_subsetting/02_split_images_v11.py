#@ File    (label = "Input directory", style = "directory") srcFile
## File    (label = "Output directory", style = "directory") dstFile
## String  (label = "File extension", value=".tif") ext
#@ String  (label = "File name contains", value = "") containString
## boolean (label = "Keep directory structure when saving", value = true) keepDirectories

import os
import copy
from ij import IJ, ImagePlus
from loci.formats import ImageReader
from loci.formats import MetadataTools
import os
import org.yaml.snakeyaml.DumperOptions as DumperOptions;
import org.yaml.snakeyaml.Yaml as Yaml;
import java.io.FileWriter as FileWriter;
import java.io.FileInputStream as FileInputStream;
from loci.common import Region
from loci.plugins.in import ImporterOptions
from loci.plugins import BF


ext = ".yaml" # hard coded to avoid confusuion
dstFolder = "02_TIF"
keepDirectories = True


def run():
	srcDir = srcFile.getAbsolutePath()
	dstDir = str(os.path.dirname(srcDir)) + "/" + dstFolder
	print(dstDir)
	if not os.path.exists(dstDir):
		os.mkdir(dstDir)
		
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
 
def process(srcDir, dstDir, currentDir, filename, keepDirectories):
	
	# Opening the local metadata file
	md_local = readYaml(srcDir + "/" + filename)

	# Get name of image
	# Name should match yaml file and ext should be the same as in md_local["metadata"]["Raw file extension"]
	img_path = os.path.splitext(filename)[0] + md_local["metadata"]["Raw file extension"]

	# Get number of channels
	nChannels = len(md_local["metadata"]["Channels"])
	
	# Open image
	#print(i)
	options = ImporterOptions()
	options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
	options.setId(srcDir + "/" + img_path)
	options.setVirtual(True)
	options.setOpenAllSeries(True)
		#options.setCBegin(i + 1, 0)
		#options.setCEnd(i + 1 , (nChannels -1)) 
	imgs = BF.openImagePlus(options)
	
	for i, img in enumerate(imgs):	
		filename_out = dstDir + "/" + os.path.splitext(filename)[0] + "_" + md_local["metadata"]["Positions"][i]
		IJ.saveAs(img, "Tiff", filename_out + ".tif")
		md_i = getMetaData_i(md_local, i)
		saveYaml(md_i, filename_out + ".yaml")
		
	# loop over channels positions/series
	#for i, pos in enumerate(md_local["metadata"]["Positions"]):

def readYaml(path):
	# Function taht reads yaml files into dict
	# Required imports
	# import org.yaml.snakeyaml.Yaml as Yaml;
	# import java.io.FileInputStream as FileInputStream;
	yaml = Yaml()
	md = yaml.load( FileInputStream(path) )
	return(md)
# md_all = readYaml("F:/ProcessingFolder/Isa_Oeyvind/00_Raw/20200610_Peri-Trim_20200604_stain_control.yaml")
# print(md_all["metadata"]["ELNID"])

def saveYaml(dictionary, path):
	# Function that saves a python dictionary
	# Needs imports:
	# import org.yaml.snakeyaml.DumperOptions as DumperOptions;
	# import org.yaml.snakeyaml.Yaml as Yaml;
	# import java.io.FileWriter as FileWriter;
	dumperOptions = DumperOptions()
	dumperOptions.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK)
	yaml = Yaml(dumperOptions)
	writer = FileWriter(path)
	yaml.dump(dictionary, writer)
	writer.flush()
	writer.close()

def getMetaData_i(md_local, i):
	md_i = copy.deepcopy(md_local) # Actual copy
	# remove Position spessific info that is not needed
	md_i["metadata"]["Image dimensions"] = str(md_i["metadata"]["Image dimensions"][i])
	md_i["metadata"]["Positions"] = str(md_i["metadata"]["Positions"][i])
	md_i["metadata"]["Sample ID"] = str(md_i["metadata"]["Sample ID"][i])
	return(md_i)

run()
