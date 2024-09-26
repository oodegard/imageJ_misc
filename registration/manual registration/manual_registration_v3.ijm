#@ File (label="Reference Image", style="file") referenceImageFile
#@ File (label="Image to Align", style="file") alignImageFile

// Function to pad an image
function padImage(imgTitle, newWidth, newHeight) {
    selectImage(imgTitle);
    originalWidth = getWidth();
    originalHeight = getHeight();

    // Calculate padding
    padLeft = floor((newWidth - originalWidth) / 2);
    padRight = newWidth - originalWidth - padLeft;
    padTop = floor((newHeight - originalHeight) / 2);
    padBottom = newHeight - originalHeight - padTop;

    // Create a canvas with the new dimensions and center the image
    run("Canvas Size...", "width=" + newWidth + " height=" + newHeight + 
        " position=[Upper Left]");
    setMinAndMax(0, 0); // Ensure zero padding
}

// Open selected images
referenceImagePath = referenceImageFile.getAbsolutePath();
alignImagePath = alignImageFile.getAbsolutePath();
open(referenceImagePath);
referenceImageTitle = getTitle();
open(alignImagePath);
alignImageTitle = getTitle();

// Determine dimensions of both images
selectImage(referenceImageTitle);
width1 = getWidth();
height1 = getHeight();

selectImage(alignImageTitle);
width2 = getWidth();
height2 = getHeight();

// Determine the larger dimensions
finalWidth = max(width1, width2);
finalHeight = max(height1, height2);

// Pad images to make them of the same size
if (width1 != finalWidth || height1 != finalHeight) {
    padImage(referenceImageTitle, finalWidth, finalHeight);
}

if (width2 != finalWidth || height2 != finalHeight) {
    padImage(alignImageTitle, finalWidth, finalHeight);
}

// Optionally save the padded images
saveAs("Tiff", getDirectory("output") + "reference_image_pad.tif");
saveAs("Tiff", getDirectory("output") + "image_align_pad.tif");
