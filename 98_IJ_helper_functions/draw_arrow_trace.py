from ij import IJ
from ij.plugin import ChannelSplitter
from ij.plugin.frame import RoiManager

## This function is used to draw a ROI in a spessiffic location in xyzct onto a hyperstack
IJ.run("Close All", "");

imp = IJ.openImage("C:/Users/oodegard/Desktop/3_RPE-1_Phafin2-GFP_MAP4K3-Halo549_3sec_001_D3D_ALX.dv");
IJ.run("Point Tool...", "type=Hybrid color=Yellow size=Small auto-next add");


# Get image
imp = IJ.getImage()

# Get Roi
rm = RoiManager.getInstance()
rm.runCommand("Associate", "true");
rm.runCommand("Centered", "false");
rm.runCommand("UseNames", "false");


## Get active channel
active_ch = imp.getC()

# The image will be flattened, so contrast is adjusted
IJ.run(imp, "Enhance Contrast", "saturated=0.01")

# Change to activbe image again
imp.setC(active_ch)
imp.show()

## get bitdepth
bd = imp.bitDepth 

# Get channel of each rm
roi_ch = []
for i, r in enumerate(rm):
	rm.select(i)
	roi_ch.append(r.getCPosition())

## Split channel
rm.runCommand(imp,"Deselect");
channels = ChannelSplitter.split(imp)

## Convert to RGB
for c in channels:
	IJ.run(c, "RGB Color", "")

# display each roi in its channel and flatten
for ch, c in enumerate(channels):
	c.show()
	# Rois to show for this channel 
	ch_rois = [i for i, e in enumerate(roi_ch) if e == ch]
	rm.setSelectedIndexes(ch_rois)
	
	crasr
	
	#for i, r in enumerate(rm):
	#	if(roi_ch[i] == ch):
	#		rm.select(i)
	#		roi = channels[active_ch -1].getRoi()
	#		rm_c.addRoi(roi)
	
	#IJ.run(imp, "Flatten", "Stack")
	
	
		
		
	#channels[active_ch -1].setRoi(r)
	#channels[active_ch -1].show()
	

	## Draw ROI
	
#roi = channels[active_ch -1].getRoi()
#rm_arrow.addRoi(roi)

#IJ.run("draw arrow", "x=100 y=100 x1=200 y1=300")
#roi = channels[active_ch -1].getRoi()
#rm_arrow.addRoi(roi)

## Display rois
#

## Convert to original bitdepth
# Done stepwise to awoid error
#IJ.run(channels[active_ch -1], "8-bit", "")

#if(bd == 16): 
#	IJ.run(channels[active_ch -1], "16-bit", "")




