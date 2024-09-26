#@ File(label="Reference Image", style="file") reference_image_file
#@ File(label="Image to Align", style="file") align_image_file

from ij import IJ, WindowManager
from ij.plugin import RGBStackMerge
from ij.process import ColorProcessor
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
import os
import threading
from javax.swing import JFrame, JButton, JLabel, BoxLayout, SwingUtilities
from java.lang import Runnable

# Ensure all windows closed before starting
IJ.run("Close All", "")

# Create an event object to wait until the dialog is done
dialog_done_event = threading.Event()

class FlipImagesDialog(JFrame):
    def __init__(self):
        super(FlipImagesDialog, self).__init__("Flip Images")
        self.initUI()

    def initUI(self):
        self.setLayout(BoxLayout(self.getContentPane(), BoxLayout.Y_AXIS))

        self.label = JLabel("Flip vertically and horizontally until correct then click OK.")
        self.add(self.label)

        self.flipVertButton = JButton("Flip Vertically")
        self.flipHorzButton = JButton("Flip Horizontally")
        self.okButton = JButton("OK")

        self.flipVertButton.addActionListener(self.flipVertically)
        self.flipHorzButton.addActionListener(self.flipHorizontally)
        self.okButton.addActionListener(self.closeDialog)

        self.add(self.flipVertButton)
        self.add(self.flipHorzButton)
        self.add(self.okButton)

        self.setSize(300, 150)
        self.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

    def flipVertically(self, event):
        imp = WindowManager.getCurrentImage()
        if imp is not None:
            IJ.run(imp, "Flip Vertically", "")

    def flipHorizontally(self, event):
        imp = WindowManager.getCurrentImage()
        if imp is not None:
            IJ.run(imp, "Flip Horizontally", "")

    def closeDialog(self, event):
        # Hide the images before closing
        imp1 = WindowManager.getImage("reference_image_title")
        imp2 = WindowManager.getImage("align_image_title")
        if imp1 is not None:
            imp1.hide()
        if imp2 is not None:
            imp2.hide()
        self.dispose()
        dialog_done_event.set()  # Signal that the dialog is closed

class ShowDialogRunnable(Runnable):
    def run(self):
        prepareImages()  # Set titles and show images
        dialog = FlipImagesDialog()  # Instantiate the dialog
        dialog.setVisible(True)  # Ensure the dialog is visible

def prepareImages():
    ids = WindowManager.getIDList()
    if ids is not None and len(ids) >= 2:
        imp1 = WindowManager.getImage(ids[0])
        imp2 = WindowManager.getImage(ids[1])
        imp1.setTitle("reference_image_title")
        imp2.setTitle("align_image_title")
        imp1.show()
        imp2.show()
        IJ.run("Tile", "")
    else:
        print("Two images need to be open.")

def pad_image(image, width_pad, height_pad, bitdepth, pad_color=0):
    ip = image.getProcessor()
    width = ip.getWidth() + abs(width_pad)
    height = ip.getHeight() + abs(height_pad)
    canvas = IJ.createImage("Temp", "{} black".format(bitdepth), width, height, 1)
    canvas_ip = canvas.getProcessor()

    # Insert the original image at the proper place to apply offset
    x_insert = max(0, width_pad)
    y_insert = max(0, height_pad)
    canvas_ip.insert(ip, x_insert, y_insert)
    canvas.setProcessor(canvas_ip)

    return canvas

def open_image_with_bioformats(path):
    options = ImporterOptions()
    options.setId(path)
    imps = BF.openImagePlus(options)
    if len(imps) > 0:
        return imps[0]
    return None

# Ensure the file paths are valid
reference_image_path = reference_image_file.getPath()
align_image_path = align_image_file.getPath()

if not (os.path.isfile(reference_image_path) and os.path.isfile(align_image_path)):
    print("Invalid file paths!")
    raise SystemExit

# Open the reference image using Bio-Formats
reference_image = open_image_with_bioformats(reference_image_path)
if reference_image is None:
    print("Failed to open reference image with Bio-Formats.")
    raise SystemExit
reference_width = reference_image.getWidth()
reference_height = reference_image.getHeight()
reference_bitdepth = reference_image.getBitDepth()

# Open the image to align using Bio-Formats
align_image = open_image_with_bioformats(align_image_path)
if align_image is None:
    print("Failed to open image to align with Bio-Formats.")
    raise SystemExit
align_width = align_image.getWidth()
align_height = align_image.getHeight()
align_bitdepth = align_image.getBitDepth()

# Ensure images are 32-bit
if reference_bitdepth != 32:
    IJ.run(reference_image, "32-bit", "")
if align_bitdepth != 32:
    IJ.run(align_image, "32-bit", "")
bitdepth = "32-bit"

# Determine the new dimensions
final_width = max(reference_width, align_width)
final_height = max(reference_height, align_height)

# Pad images to make them of the same size if necessary
if reference_width != final_width or reference_height != final_height:
    padded_reference_image = pad_image(reference_image, final_width - reference_width, final_height - reference_height, bitdepth)
else:
    padded_reference_image = reference_image

if align_width != final_width or align_height != final_height:
    padded_align_image = pad_image(align_image, final_width - align_width, final_height - align_height, bitdepth)
else:
    padded_align_image = align_image

# Ask the user to flip the images
padded_reference_image.show()
padded_align_image.show()

# Run the ShowDialogRunnable on the Swing event dispatch thread
SwingUtilities.invokeLater(ShowDialogRunnable())

# Wait for the dialog to be closed
dialog_done_event.wait()  # Wait here until the dialog sets the event

padded_reference_image.hide()
padded_align_image.hide()

# Continue with the rest of your processing
combined_stack = RGBStackMerge.mergeChannels([padded_reference_image, padded_align_image], True)
combined_stack.show()




