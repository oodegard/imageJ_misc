#@ File    (label = "Input directory", style = "directory") srcFile
## File    (label = "Output directory", style = "directory") dstFile
#@ String  (label = "Lab book ID") ELNID
#@ String  (label = "File extension", value=".lif") ext
#@ String  (label = "File name contains (Nothing means all)", value = "") containString
#@ String  (label = "Species name", value="Human") speciesName
#@ String  (label = "Species taxon", value="9606") speciesTaxon
#@ String  (label = "Strain (Cell line)") strain
#@ String  (label = "Labels") labels


srcDir = srcFile.getAbsolutePath()
dstDir = srcDir

#path = "F:/ProcessingFolder/Isa_Oeyvind/00_Raw/20200610_Peri-Trim_20200604_stain_control.lif"

from loci.formats import ImageReader
from loci.formats import MetadataTools
import os
import org.yaml.snakeyaml.DumperOptions as DumperOptions;
import org.yaml.snakeyaml.Yaml as Yaml;
import java.io.FileWriter as FileWriter;
import java.io.FileInputStream as FileInputStream;

from ij.gui import WaitForUserDialog


def run():
	srcDir = srcFile.getAbsolutePath().replace("\\", "/")
  	# Make local yaml metadata files next to each image file matching ext
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort()
		for filename in filenames:
			# Check for file extension
			if not filename.endswith(ext):
				continue
			# Check for file name pattern
			if containString not in filename:
				continue
			get_metadata(srcDir, filename, dstDir) #(srcDir, root, filename, keepDirectories)
	# Make global yaml metadata file based on all local yaml metadata files
	path_global_metadata = os.path.dirname(srcDir) + "/" + ELNID + "_global_metadata.yaml"
	# print(path_global_metadata)
	path_local_metadata = []
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort()
		for filename in filenames:
			# Check for file extension
			if not filename.endswith(".yaml"):
				continue
			# Check for file name pattern
			if containString not in filename:
				continue
  			path_local_metadata.append(srcDir + "/" + str(filename))
  	makeGlobalMetadata(path_global_metadata, path_local_metadata)

	# Wait for user to edit global metadata file
  	myWait = WaitForUserDialog("Edit global metadata file Channel info", "You can edit global metadata 'Channels' now,\nRember to save!, and then press 'OK' to updata local metadata files")
	myWait.show()

	# Updata local metadata files with Sample ID from global metadata file
	md_global = readYaml(path_global_metadata)
	
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort()
		for filename in filenames:
			# Check for file extension
			if not filename.endswith(".yaml"):
				continue
			# Check for file name pattern
			if containString not in filename:
				continue
			updateLocalMetadata(path_global_metadata, srcDir + "/" + filename)

def get_metadata(srcDir, filename, dstDir):
	path = srcDir + "/" + filename
	idx = filename.rindex('.')
	filenameSansExt = filename[0:idx]
	#print(filenameSansExt)
	
	reader = ImageReader()
	omeMeta = MetadataTools.createOMEXMLMetadata()
	reader.setMetadataStore(omeMeta)
	reader.setId(path)

	# Get physical pixel size
	X_um = omeMeta.getPixelsPhysicalSizeX(0).value()
	Y_um = omeMeta.getPixelsPhysicalSizeY(0).value()
	Z_um = omeMeta.getPixelsPhysicalSizeZ(0).value()
	#T_um = omeMeta.getPixelsPhysicalSizeT(0).value()

	# count number of series in file
	seriesCount = reader.getSeriesCount()
	
	dim = []
	for s in range(seriesCount):
		reader.setSeries(s)
		# Get series info
		# seriesMetadata = reader.getSeriesMetadata()
		# globalMetadata = reader.getSeriesMetadata()
		# print(dir(globalMetadata));
		
		# Get image dims
		X = reader.getSizeX() 
		Y = reader.getSizeY() 
		Z = reader.getSizeZ() 
		C = reader.getSizeC() 
		T = reader.getSizeT() 
		dim.append("x".join([str(X), str(Y), str(Z), str(C), str(T)]))
	# print(dim)

	#X_um = globalMetadata.getPixelsPhysicalSizeX()
	
	# Get number of series
	seriesCount = reader.getSeriesCount()

	# Get channel names
	keys = range(C)
	names = ["Channel " + str(i+1) for i in keys]
	channels = [{"Channel " + str(i+1) : {"Entity": "NA", "label": "NA"}} for i in keys] 

	# Get timepoint names
	keys = range(T)
	timepoints = ["Time_" + '{:05d}'.format(i+1) for i in keys]

	# Get position names
	keys = range(seriesCount)
	positions = ["Pos_" + '{:05d}'.format(i+1) for i in keys]

	# Species

	
	# Make dictionary of yaml file
	yml = {
		"metadata": {
			"ELNID": ELNID,
			"Total data size": os.stat(path).st_size,
			"Raw file extension": os.path.splitext(filename)[1],
			"Image dimensions": dim,
			"Physical dimensions": {
				"X_um": X_um,
				"Y_um": Y_um,
				"Z_um": Z_um
			},
			"Channels": channels,
			"Time points": timepoints,
			"Positions": positions,
			"Sample ID": [p + "_ID" for p in positions],
			"Species": {"Name": speciesName, "Taxon": speciesTaxon},
			#"Developmental stage": devStage,
			"Strain": strain,
			"labels": labels
		}
	}
	# print(yml)
	saveYaml(yml, dstDir + "/" + filenameSansExt + ".yaml")

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


# function to get unique values 

def unique(seq):
   # not order preserving
   set = {}
   map(set.__setitem__, seq, [])
   return sorted(set.keys())


def makeGlobalMetadata(path_global_metadata, path_local_metadata):
	md_all = [readYaml(yl) for yl in path_local_metadata]
	md_global = {
		"metadata": {
			"Physical dimensions": [md["metadata"]["Physical dimensions"] for md in md_all][0], # [0] to Keep first only
			#"Time points": unique([str(item) for sublist in [md["metadata"]["Time points"] for md in md_all] for item in sublist]), # Single sorted list, only unique
			"Channels": [md["metadata"]["Channels"] for md in md_all][0], # [0] to Keep first only
			#"Image dimensions": unique([md["metadata"]["Image dimensions"] for md in md_all])[0], # [0] to Keep first only
			#"Strain": unique([str(md["metadata"]["Strain"]) for md in md_all])[0], #[0] to Keep first only
			"ELNID": unique([str(md["metadata"]["ELNID"]) for md in md_all])[0], #[0] to Keep first only
			#"Positions": unique([str(item) for sublist in [md["metadata"]["Positions"] for md in md_all] for item in sublist]),
			#"Sample ID": unique([str(item) + "_ID" for sublist in [md["metadata"]["Positions"] for md in md_all] for item in sublist]),
			#"Developmental stage": unique([str(md["metadata"]["Developmental stage"]) for md in md_all]),
			#"Total data size": unique([str(md["metadata"]["Total data size"]) for md in md_all]),
			"Species": [md["metadata"]["Species"] for md in md_all][0] #[0] to Keep first only
		}
	}
	saveYaml(md_global, path_global_metadata)

def updateLocalMetadata(md_global_path, md_local_path):
	md_global =  readYaml(md_global_path)
	md_local = readYaml(md_local_path)

	# Get values from global yaml
	#ids = [str(md_global["metadata"]["Sample ID"][md_global["metadata"]["Positions"].index(pos)]) for pos in md_local["metadata"]["Positions"]]
	channels = md_global["metadata"]["Channels"]
	
	# Set values to local yaml
	# md_local["metadata"]["Sample ID"] = ids
	md_local["metadata"]["Channels"] = channels
	saveYaml(md_local, md_local_path)


# Run program
run()


#reader.setSeries(0)
#globalMetadata = reader.getSeriesMetadata()
#print(globalMetadata);
#reader.close()