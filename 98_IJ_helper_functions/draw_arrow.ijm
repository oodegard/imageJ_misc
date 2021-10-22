#@ Integer(label = "x") x1
#@ Integer(label = "y") y1
#@ Integer(label = "x1") x2
#@ Integer(label = "y1") y2

function drawArrow(x1,y1,x2,y2) {
	run("Select None");
	eval('script','img = IJ.getImage();a= new Arrow('+x1+','+y1+','+x2+','+y2+');img.setRoi(a);');
}

drawArrow(x1,y1,x2,y2);




