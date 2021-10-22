/*
 * This macro Adds an arrow to all ROIs in the ROI Manager
 * By Øyvind Ødegård Fougner
 * oodegard@gmail.com
 */


arrow_width =  2;
arrow_size = 10;
arrow_color = "white";
arrow_style = "Filled";
arrow_outline = false;
arrow_double_head = false;
arrow_keep_after_overlay = false;
x_offset = 10; // Pixels
y_offset = 10; // Pixels


function drawArrow(x,y,x1,y1) {1
	run("Select None");
	eval('script','img = IJ.getImage();a= new Arrow('+x+','+y+','+x1+','+y1+');img.setRoi(a);');
}

function makeArrow() {
	getSelectionCoordinates(x, y);
	drawArrow(x[0] + x_offset, y[0] - y_offset, x[0] + 2, y[0] - 2);
	Roi.setStrokeColor(arrow_color);	
	run("Draw", "slice");
	run("Select None");
}


function processWindow(){
	// Adds an arrow to all multipoints in stack
	
	// Setup
	roiManager("Show All without labels");

	// Run
	run("Duplicate...", "duplicate");
	run("RGB Color");
	
	
	count = roiManager("count");
	current = roiManager("index");
	for (i = 0; i < count; i++) {
		roiManager("select", i);
		makeArrow();
		//roiManager("update");
	}
	if (current < 0)
		roiManager("deselect");
	else
		roiManager("select", current);
}

processWindow();