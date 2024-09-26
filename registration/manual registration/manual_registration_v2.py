from ij import WindowManager
from ij.gui import GenericDialog

# Function to get window position
def get_window_position(image):
    location = image.getWindow().getLocationOnScreen()
    return (location.x, location.y)

# Fetch the current windows for the channels
image1 = WindowManager.getImage(WindowManager.getImageTitles()[0])
image2 = WindowManager.getImage(WindowManager.getImageTitles()[1])

# Get their positions
pos1 = get_window_position(image1)
pos2 = get_window_position(image2)

# Calculate the relative shift
shift_x = pos2[0] - pos1[0]
shift_y = pos2[1] - pos1[1]

# Display the results using the 'format' method
gd = GenericDialog("Alignment Result")
gd.addMessage("Channel 1 Position: ({}, {})".format(pos1[0], pos1[1]))
gd.addMessage("Channel 2 Position: ({}, {})".format(pos2[0], pos2[1]))
gd.addMessage("Shift Required: (x: {}, y: {})".format(shift_x, shift_y))
gd.showDialog()
