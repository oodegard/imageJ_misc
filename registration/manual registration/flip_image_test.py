from ij import IJ, WindowManager
from javax.swing import JFrame, JButton, JLabel, BoxLayout, SwingUtilities
from java.lang import Runnable

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
        self.setVisible(True)
    
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

class ShowDialogRunnable(Runnable):
    def run(self):
        prepareImages()  # Set titles and show images
        FlipImagesDialog()  # Show the dialog

# This function will ensure the images are shown with specific titles
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

# Run the ShowDialogRunnable on the Swing event dispatch thread
SwingUtilities.invokeLater(ShowDialogRunnable())
