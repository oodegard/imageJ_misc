#@ String (label="Select LUT", choices={"Fire", "Fire_inv", "mpl-viridis", "Rainbow RGB"}, value="Fire") glut
#@ Integer (label="Start frame", value=1, min=1 ) gstartf
#@ Integer (label="End frame (-1 means all frames)", value=-1, min=-1) gendf
#@ Integer (label="Create Time Color Scale Bar?", value = 1, min = 0, max = 1) gframecolorscale
#@ Integer (label="Batch mode? (no image output)", value = 1, min = 0, max = 1) gbatchmode

// glut:: Any colour from getList("LUTs"); can be added to choices and then selected

contrast_saturated = 0;


// By: Øyvind Ødegård Fougner (oyvinode@uio.no)
// based on temporal color-code by
// Kota Miura (miura@embl.de)
// Centre for Molecular and Cellular Imaging, EMBL Heidelberg, Germany 

// This script runs on the active window
// Needs to have a single channel
// Needs to have a single z-plane

// Can be called in imageJ macro language by:
// run("temporal color code channel") // Will open for user input
// run("temporal color code channel", "glut=[Fire], gstartf=[1], gendf=[-1], gframecolorscale=[1], gbatchmode=[1]"); // Will run headless

macro "colorCode"{ 
// Add temporal colour code to stack
	
	
	if(nImages == 0)
		exit("No open images");
	run("Enhance Contrast", "saturated=" + contrast_saturated);
	// Setup
	Stack.getDimensions(ww, hh, channels, slices, frames);
	
	//// set end slice to max if gendf == -1
	if (gendf == -1)
		gendf = frames;

	//// reduce gendf if larger than number of frames
	if(gendf > frames)
		gendf = frames;
	
	//// Exit if not a stack
	if (channels > 1){
		exit("Cannot color-code multi-channel images!");
	}
		
	
	if (frames < 2){
		exit("Cannot color-code single-frame image!");
	}
		
	
	if(gbatchmode){
		setBatchMode(true);
	}
		

	// Make temporal color image
	totalframes = gendf - gstartf + 1;
	calcslices = slices * totalframes;
	imgID = getImageID();

	newImage("colored", "RGB White", ww, hh, calcslices);
	run("Stack to Hyperstack...", "order=xyczt(default) channels=1 slices="
		+ slices + " frames=" + totalframes + " display=Color");
	newimgID = getImageID();

	selectImage(imgID);
	run("Duplicate...", "duplicate");
	run("8-bit");
	imgID = getImageID();

	newImage("stamp", "8-bit White", 10, 10, 1);
	run(glut);
	getLut(rA, gA, bA);
	close();
	nrA = newArray(256);
	ngA = newArray(256);
	nbA = newArray(256);

	newImage("temp", "8-bit White", ww, hh, 1);
	tempID = getImageID();

	for (i = 0; i < totalframes; i++) {
		colorscale = floor((256 / totalframes) * i);
		for (j = 0; j < 256; j++) {
			intensityfactor = j / 255;
			
			//intensityfactor = intensityfactor * (1 + -1*pow(intensityfactor, 2)) ; // This reduces the intensity at high intensity = things that does not move
			nrA[j] = round(rA[colorscale] * intensityfactor);
			ngA[j] = round(gA[colorscale] * intensityfactor);
			nbA[j] = round(bA[colorscale] * intensityfactor);		
		}

		for (j = 0; j < slices; j++) {
			selectImage(imgID);
			Stack.setPosition(1, j + 1, i + gstartf);
			run("Select All");
			run("Copy");

			selectImage(tempID);
			run("Paste");
			setLut(nrA, ngA, nbA);
			run("RGB Color");
			run("Select All");
			run("Copy");
			run("8-bit");

			selectImage(newimgID);
			Stack.setPosition(1, j + 1, i + 1);
			run("Select All");
			run("Paste");
		}
	}

	selectImage(tempID);
	close();

	selectImage(imgID);
	close();

	selectImage(newimgID);

	run("Stack to Hyperstack...", "order=xyctz channels=1 slices="
		+ totalframes + " frames=" + slices + " display=Color");
	op = "start=1 stop=" + gendf + " projection=[Max Intensity] all";
	run("Z Project...", op);
	if (slices > 1)
		run("Stack to Hyperstack...", "order=xyczt(default) channels=1 slices=" + slices
			+ " frames=1 display=Color");
	resultImageID = getImageID();

	selectImage(newimgID);
	close();

	selectImage(resultImageID);
	
	// Exit batchmode
	if(gbatchmode)
		setBatchMode("exit and display");

	// Make colour scale
	if(gframecolorscale)
		CreateScale(glut, gstartf, gendf);

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
