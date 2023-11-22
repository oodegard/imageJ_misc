/*
 * Macro template to process multiple images in a folder
 */

#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix
// boolean (label = "First series only") firstOnly

firstOnly = true;
batchmode = true;
// See also Process_Folder.py for a version of this code
// in the Python scripting language.




processFolder(input);

// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	print("Processing folder: " + input );
	
	if(batchmode){
		setBatchMode("hide");
	}
	
	
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i]);
	}
	
	if(batchmode){
		setBatchMode("exit and display");
	}
}

function processFile(input, output, file) {
	
	
	
	// If the input file is a tif file and input == output the input file will be overwritten and this is not alowed
	if (endsWith(file, ".tif") && input != output) {
		return "-1";
		
	}
	
	
	// Open file
	if(firstOnly){
		run("Bio-Formats Importer", "open=[" + input + File.separator +  file +"] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack");
		file_noext =File.getNameWithoutExtension(file);
	}
	// Add else if you need to process multiposition files
	
	
	// save file
	outName = file_noext + "_test.tif";
	save(output + File.separator + outName);
	print("File saved as: " + outName);
	run("Close");
	

}
