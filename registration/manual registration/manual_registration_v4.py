import napari
from napari.qt import thread_worker
import numpy as np
from PIL import Image
from qtpy.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QWidget
from scipy.ndimage import affine_transform


# Define paths to images
reference_image_path = r"C:\Users\Øyvind\OneDrive - Universitetet i Oslo\Work\03_UiO\15_instrument_data\Odyssey\0000011_01_129_SDS_gel_halobeads_hisBeads_Comassie\0000011_01_700.TIF"
align_image_path = r"C:\Users\Øyvind\OneDrive - Universitetet i Oslo\Work\03_UiO\15_instrument_data\Odyssey\0000009_01_129_SDS_gel_halobeads_hisBeads_agfp-JF650\0000009_01_700.TIF"

# Load images
reference_image = np.array(Image.open(reference_image_path).convert('F'))
align_image = np.array(Image.open(align_image_path).convert('F'))

# Pad images to the size of the largest image
def pad_image(image, target_shape):
    padded_image = np.zeros(target_shape, dtype=image.dtype)
    padded_image[:image.shape[0], :image.shape[1]] = image
    return padded_image

final_shape = (max(reference_image.shape[0], align_image.shape[0]),
               max(reference_image.shape[1], align_image.shape[1]))

reference_image_padded = pad_image(reference_image, final_shape)
align_image_padded = pad_image(align_image, final_shape)

# Functions to flip images individually
def flip_horizontally(layer):
    layer.data = np.fliplr(layer.data)

def flip_vertically(layer):
    layer.data = np.flipud(layer.data)

# Function to save images as a composite TIFF
def save_composite_image(ref_layer, align_layer):
    # Gather current transformations from Napari
    ref_transform = ref_layer.affine.affine_matrix
    align_transform = align_layer.affine.affine_matrix

    # Remove translation part by extracting the rotation and scaling part of the affine matrix (top left 2x2)
    ref_rotation_scaling = ref_transform[:2, :2]
    ref_translation = ref_transform[:2, 2]
    
    align_rotation_scaling = align_transform[:2, :2]
    align_translation = align_transform[:2, 2]
    
    # Apply transformations
    ref_transformed_image = affine_transform(ref_layer.data, ref_rotation_scaling, offset=ref_translation)
    align_transformed_image = affine_transform(align_layer.data, align_rotation_scaling, offset=align_translation)

    # Open a file dialog to select save path
    dialog = QFileDialog()
    dialog.setDefaultSuffix("tif")
    save_path, _ = dialog.getSaveFileName(None, "Save Composite Image", "", "TIFF files (*.tif)")

    if save_path:
        ref_data = ref_transformed_image.astype(np.uint8)  # Ensure data type is uint8 for Pillow compatibility
        align_data = align_transformed_image.astype(np.uint8)

        ref_image = Image.fromarray(ref_data)
        align_image = Image.fromarray(align_data)
        
        # Save as multi-page TIFF
        ref_image.save(save_path, save_all=True, append_images=[align_image], compression="tiff_deflate")
        print(f"Composite image saved to {save_path}")
    else:
        print("Save operation cancelled")

# Initialize viewer
viewer = napari.Viewer()
reference_layer = viewer.add_image(reference_image_padded, name='reference_image')
align_layer = viewer.add_image(align_image_padded, name='align_image', colormap='red', blending='additive')

# Adding buttons with event handlers
def add_buttons(viewer):
    container = QWidget()
    layout = QVBoxLayout()

    btn_flip_h_ref = QPushButton('Flip Reference Horizontally')
    btn_flip_v_ref = QPushButton('Flip Reference Vertically')
    btn_flip_h_align = QPushButton('Flip Align Horizontally')
    btn_flip_v_align = QPushButton('Flip Align Vertically')
    btn_save = QPushButton('Save Composite Image')

    # Connect buttons to flip functions
    btn_flip_h_ref.clicked.connect(lambda: flip_horizontally(reference_layer))
    btn_flip_v_ref.clicked.connect(lambda: flip_vertically(reference_layer))
    btn_flip_h_align.clicked.connect(lambda: flip_horizontally(align_layer))
    btn_flip_v_align.clicked.connect(lambda: flip_vertically(align_layer))
    btn_save.clicked.connect(lambda: save_composite_image(reference_layer, align_layer))

    layout.addWidget(btn_flip_h_ref)
    layout.addWidget(btn_flip_v_ref)
    layout.addWidget(btn_flip_h_align)
    layout.addWidget(btn_flip_v_align)
    layout.addWidget(btn_save)
    container.setLayout(layout)
    viewer.window.add_dock_widget(container, area='right')

add_buttons(viewer)

# Start Napari
napari.run()