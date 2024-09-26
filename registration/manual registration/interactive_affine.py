#@ ImagePlus imp

from ij import IJ, ImageStack, ImagePlus
from ij.gui import Overlay, PointRoi
from ij.plugin import ChannelSplitter, RGBStackMerge
from ij.process import FloatProcessor
import java.awt.event.MouseAdapter as MouseAdapter
import java.awt.event.MouseEvent as MouseEvent

# Define global variables
points = []

# Mouse callback function to capture points
class PointCollector(MouseAdapter):
    def __init__(self, image, overlay):
        self.image = image
        self.overlay = overlay
        self.points = []
        self.dragging = None
    
    def mousePressed(self, event):
        x, y = event.getX(), event.getY()
        ox, oy = self.image.getCanvas().offScreenX(x), self.image.getCanvas().offScreenY(y)
        for point in self.points:
            if point.contains(ox, oy):
                self.dragging = point
                break
        
    def mouseDragged(self, event):
        if self.dragging is not None:
            x, y = event.getX(), event.getY()
            ox, oy = self.image.getCanvas().offScreenX(x), self.image.getCanvas().offScreenY(y)
            self.dragging.setPosition(ox, oy)
            self.image.updateAndDraw()
    
    def mouseReleased(self, event):
        if self.dragging is not None:
            self.dragging = None
        if len(self.points) == 3:
            print("Three points selected:", [(point.getXBase(), point.getYBase()) for point in self.points])

# Add three initial points on the image
overlay = Overlay()
initial_positions = [(50, 50), (100, 50), (50, 100)]  # Adjust initial positions as necessary

for pos in initial_positions:
    point = PointRoi(pos[0], pos[1])
    overlay.add(point)
    points.append(point)

imp.setOverlay(overlay)

# Add mouse listener to collect points
point_collector = PointCollector(imp, overlay)
point_collector.points = points
imp.getCanvas().addMouseListener(point_collector)
imp.getCanvas().addMouseMotionListener(point_collector)

IJ.log("Drag the 3 points to desired locations directly on the image")

# Wait until 3 points are collected
while len(point_collector.points) < 3:
    IJ.wait(100)

# Points collected by the user
pts1 = [(point.getXBase(), point.getYBase()) for point in point_collector.points]
pts2 = [(0, 0), (imp.getWidth()-1, 0), (0, imp.getHeight()-1)]

# Split the channels
channels = ChannelSplitter.split(imp)
channel1 = channels[0]
channel2 = channels[1]

# Calculate affine transformation matrix
def get_affine_matrix(pts1, pts2):
    x1, y1 = pts1[0]
    x2, y2 = pts1[1]
    x3, y3 = pts1[2]

    u1, v1 = pts2[0]
    u2, v2 = pts2[1]
    u3, v3 = pts2[2]

    A = [
        [x1, y1, 1, 0, 0, 0],
        [0, 0, 0, x1, y1, 1],
        [x2, y2, 1, 0, 0, 0],
        [0, 0, 0, x2, y2, 1],
        [x3, y3, 1, 0, 0, 0],
        [0, 0, 0, x3, y3, 1]
    ]

    B = [u1, v1, u2, v2, u3, v3]

    return [v for sublist in [list(map(lambda x: round(x, 6), row)) for row in (java.util.Arrays.asList(*java.lang.reflect.Array.newInstance(java.lang.Math, [2, 3]), A, B))] for v in sublist] + [0, 0, 1]

affine_matrix = get_affine_matrix(pts1, pts2)

# Apply affine transform to the second channel
channel2_processor = FloatProcessor(channel2.getProcessor())
channels[1] = channel2_processor.clone()
channels[1].copyBits(channel2_processor, 0, 0, affine_matrix)

# Recombine channels into a composite image
composite = RGBStackMerge.mergeChannels(channels, False)
composite.setTitle("Transformed Composite")
composite.show()

# Save the transformed composite
IJ.saveAs(composite, "Tiff", "transformed_composite_image.tif")
