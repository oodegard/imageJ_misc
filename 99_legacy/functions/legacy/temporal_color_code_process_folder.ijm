#@ String(visibility="MESSAGE", value="Select folder and pattern") text1
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix
#@ String(visibility="MESSAGE", value="Temporal color code settings") text2
#@ String (label="Select LUT", choices={"Fire", "mpl-viridis", "Rainbow RGB", }, value="Fire") glut_f
#@ Integer (label="Start frame", value=1, min=1 ) gstartf_f
#@ Integer (label="End frame (-1 means all frames)", value=-1, min=-1) gendf_f
#@ Integer (label="Create Time Color Scale Bar", min = 0, max = 1) gframecolorscale_f
// See also Process_Folder.py for a version of this code
// in the Python scripting language.


if(output == input){
	exit("Input and output folder can not be the same")
}

// Needs to have all images closed to process multipos?
run("Close All");
	
processFolder(input);

// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i]);
	}
}

function processFile(input, output, file) {
	// Do the processing here by adding your own code.
	// Leave the print statements until things work, then remove them.
	print("Processing: " + input + File.separator + file);

	output_name = File.getNameWithoutExtension(file);

	if(!File.exists(output + File.separator + output_name + "_temporal_merge.tif")){
		run("Bio-Formats Importer", "open=[" + input + File.separator + file + "] color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack");
		getPixelSize(unit, pixelWidth, pixelHeight);
		run("temporal color code process multichannel", "glut_mc=[" + glut_f + "], gstartf_mc=[" + gstartf_f + "], gendf_mc=[" + gendf_f + "], gframecolorscale_mc=[" + gframecolorscale_f + "]"); // Will run headless
	
		// Output
		output_name = File.getNameWithoutExtension(file);
		print("Saving to: " + output + File.separator + output_name );
		
		selectWindow("temporal_merge");
		setVoxelSize(pixelWidth, pixelHeight, 1, unit);
		saveAs("Tiff", output + File.separator + output_name + "_temporal_merge.tif");
	
		if(gframecolorscale_f){
			selectWindow("color time scale");
			saveAs("Tiff", output + File.separator + output_name + "_temporal_merge_scale.tif");
		}
		run("Close All");		
	}
		

}
