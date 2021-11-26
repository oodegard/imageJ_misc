#@ String (visibility=MESSAGE, value="Input to merge files", required=false) msg1
#@ File (label = "Any file from the correct directory", style = "file") example_file_name
#@ String (label = "Merge files that contains string E.g. '_visit_*_D3D.dv'" ) contains
#@ String (label = "Value to be inserted at star per group E.g. '1,2,3,4,5,6,7'" ) star_replace_values_str
#@ String (visibility=MESSAGE, value="Input for output", required=false) msg2
#@ File (label = "Output directory", style = "directory") output_folder
#@ String (label = "Output base name E.g. 'someName_*_D3D_merge.tif'" ) out_name_base
// Open files

// name a fine in the same folder that you want to extract from
// example_file_name = "G:/My Drive/05_Microscope_images/20211124_four_col_exchange/Raw/20211124_four_col_exchange_01_Golgi_001_visit_2_D3D.dv";

// A pattern that all files you want to open has
//contains = "_visit_*_D3D.dv";

// output name 
// place a star for star_replace_values to appear
out_path_base = output_folder + File.separator + out_name_base // "G:/My Drive/05_Microscope_images/20211124_four_col_exchange/Analysis/20211124_four_col_exchange_visit_*_D3D_merge.tif"

star_replace_values = split(star_replace_values_str, ","); 

for (i = 0; i < star_replace_values.length; i++) {
	rep = star_replace_values[i];
	cont = replace(contains, "*", rep);

	// Open
	run("Bio-Formats Importer", "open=[" + example_file_name + "] color_mode=Default group_files rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT use_virtual_stack file_name axis_1_number_of_images=2 axis_1_axis_first_image=1 axis_1_axis_increment=1 axis_2_number_of_images=7 axis_2_axis_first_image=1 axis_2_axis_increment=1 contains=" + cont);

	// Correct 3D drift
	run("Correct 3D drift", "channel=1 only=0 lowest=1 highest=33 max_shift_x=10.000000000 max_shift_y=10.000000000 max_shift_z=10.000000000");
	close("\\Others");

	// Save
	out_name = replace(out_path_base, "*", star_replace_values[i]);
	saveAs("Tiff", out_name);

	run("Close All");
}



