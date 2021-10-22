#@ String (label="Select LUT", choices={"Fire", "Fire_inv", "mpl-viridis", "Rainbow RGB"}, value="Fire") glut
#@ Integer (label="Start frame", value=1, min=1 ) gstartf_mc
#@ Integer (label="End frame (-1 means all frames)", value=-1, min=-1 ) gendf_mc
#@ Integer (label="Create Time Color Scale Bar?", min = 0, max = 1) gframecolorscale_mc
// Integer (label="Batch mode? (no image output)", value = 1, min = 0, max = 1) gbatchmode

print("gframecolorscale_mc: " + gframecolorscale_mc);

// glut_mc:: Any colour from getList("LUTs"); can be added to choices and then selected

// By: Øyvind Ødegård Fougner (oyvinode@uio.no)
// based on temporal color-code by
// Kota Miura (miura@embl.de)
// Centre for Molecular and Cellular Imaging, EMBL Heidelberg, Germany 

// This script runs on the active window
// Loops trough all channels and merges the output into a hyperstack
// Will make a z-project if several z-planes are found


macro "Time-Lapse Color Coder" {
	if(nImages == 0)
		exit("No open images");
	
	Stack.getDimensions(source_ww, source_hh, source_channels, source_slices, source_frames);

	// set end slice to max if gendf_mc == -1
	if (gendf_mc == -1)
		gendf_mc = source_frames;

	// reduce gendf_mc if larger than number of frames
	if(gendf_mc > source_frames)
		gendf_mc = source_frames;
	
	if (source_frames < 2)
		exit("Cannot color-code single-frame image!");
	
	if(source_slices > 1){
		run("Z Project...", "projection=[Max Intensity] all");
		rename("MAX_source");
	}
	source_imgTitle = getTitle();	
	selectWindow(source_imgTitle);
	

	concatString = "";
	for (ch = 0; ch < source_channels; ch++) {
		selectWindow(source_imgTitle);
		run("Duplicate...", "title=ch" + ch+1 + " duplicate channels=" + ch+1);
		
		selectWindow("ch" + ch+1);

		run("temporal color code", "glut=[" + glut_mc + "], gstartf=[" + gstartf_mc + "], gendf=[" + gendf_mc + "], gframecolorscale=[0], gbatchmode=[1]"); // Will run headless
		
		// remame tmp ch image
		selectWindow("ch" + ch+1);
		rename("_ch" + ch+1);
		
		// rename output
		selectWindow("MAX_colored");
		rename("ch_col" + ch+1);

		// make concatination string
		concatString = concatString + "image" + ch+1 + "=ch_col" + ch+1 + " ";
	}

	
	// run("Concatenate...", "  image1=ch1 image2=ch2 image3=[-- None --]");
	if(source_channels > 1){
		run("Concatenate...", concatString);

		//run("Make Montage...", "columns=" + source_channels + " rows=1 scale=1");
	}
	rename("temporal_merge");

	if(source_slices > 1){
		selectWindow("MAX_source");
		run("Close");
	}

	
	if (gframecolorscale_mc){
		CreateScale(glut_mc, gstartf_mc, gendf_mc);	
	}
		
}

function CreateScale(lutstr, beginf, endf){
	ww = 256;
	hh = 32;
	newImage("color time scale", "8-bit White", ww, hh, 1);
	for (j = 0; j < hh; j++) {
		for (i = 0; i < ww; i++) {
			setPixel(i, j, i);
		}
	}
	run(lutstr);
	run("RGB Color");
	op = "width=" + ww + " height=" + (hh + 16) + " position=Top-Center zero";
	run("Canvas Size...", op);
	setFont("SansSerif", 12, "antiliased");
	run("Colors...", "foreground=white background=black selection=yellow");
	drawString("frame", round(ww / 2) - 12, hh + 16);
	drawString(leftPad(beginf, 3), 0, hh + 16);
	drawString(leftPad(endf, 3), ww - 24, hh + 16);

}
function leftPad(n, width) {
    s = "" + n;
    while (lengthOf(s) < width)
        s = "0" + s;
    return s;
}