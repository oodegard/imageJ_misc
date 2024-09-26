#@ File(label="Reference Image", style="file") reference_image_file
#@ File(label="Image to Align", style="file") align_image_file
from ij import IJ, WindowManager
from ij.plugin import RGBStackMerge
from ij.process import ColorProcessor
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from ij.gui import WaitForUserDialog, GenericDialog
import os

IJ.run("Close All", "")

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

# Ensure images are 32-bit (or 16-bit if preferred)
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

padded_reference_image.show()
padded_align_image.show()

# Alignment functionality
def get_window_position(image):
    location = image.getWindow().getLocationOnScreen()
    return (location.x, location.y)

# Fetch the current windows for the images
reference_image = WindowManager.getImage(padded_reference_image.getTitle())
align_image = WindowManager.getImage(padded_align_image.getTitle())

# Inform the user to manually align images using WaitForUserDialog
wait_dialog = WaitForUserDialog("Manual Alignment", "Please manually align the image windows by dragging them. Click OK when done.")
wait_dialog.show()

# Get their positions after manual alignment
pos_ref = get_window_position(reference_image)
pos_align = get_window_position(align_image)

# Calculate the relative shift
shift_x = pos_align[0] - pos_ref[0]
shift_y = pos_align[1] - pos_ref[1]

# Adjusting the padding of both images based on the calculated offset
padded_ref_with_offset = pad_image(padded_reference_image, -shift_x if shift_x < 0 else 0, -shift_y if shift_y < 0 else 0, bitdepth)
padded_align_with_offset = pad_image(padded_align_image, shift_x if shift_x > 0 else 0, shift_y if shift_y > 0 else 0, bitdepth)

# Combine the images into a new composite image
combined_stack = RGBStackMerge.mergeChannels([padded_ref_with_offset, padded_align_with_offset], True)
combined_stack.show()

# Display the results using the 'format' method
gd = GenericDialog("Alignment Result")
gd.addMessage("Reference Image Position: ({}, {})".format(pos_ref[0], pos_ref[1]))
gd.addMessage("Image to Align Position: ({}, {})".format(pos_align[0], pos_align[1]))
gd.addMessage("Shift Required: (x: {}, y: {})".format(shift_x, shift_y))
gd.showDialog()
