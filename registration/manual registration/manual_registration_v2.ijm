/* Macro tool to move, scale, and rotate channels in multichannel images with sub-pixel resolution
 * Nicolas De Francesco - March 2020
 * Updated: September 2024 by Øyvind Ødegård Fougner
 */


/*
 * Macro tool for moving, scaling, and rotating channels in multichannel images with sub-pixel resolution.
 * Created by Nicolas De Francesco - March 2020
 * Updated by [Your Name] - September 2024
 * 
 * Description:
 * This macro allows you to move, scale, and rotate individual channels in multichannel images with precision.
 * It is useful for correcting misalignments or for fine-tuning images with multiple channels.
 * 
 * Installation Instructions:
 * 1. Open ImageJ/Fiji.
 * 2. Go to `Plugins` > `Macros` > `New...` to open the macro editor.
 * 3. Copy and paste the entire macro code into the editor.
 * 4. Save the macro with a descriptive name (e.g., `MoveScaleRotateChannels.ijm`).
 * 5. Close the macro editor.
 * 
 * Usage Instructions:
 * 1. Open the multichannel image you wish to adjust.
 * 2. Run the macro by going to `Plugins` > `Macros` > `Run...` and select the saved macro file.
 * 3. To create a working copy of the image, press the `F5` key. This will create a duplicate of the current image titled "corrected-[original title]".
 * 4. To move a channel:
 *    - Select the "Move channels Tool" from the macro.
 *    - Click and drag on the channel you want to move in the duplicated image.
 *    - Hold `Ctrl` to amplify the movement if needed.
 * 5. To adjust tool settings (e.g., step multipliers, scaling factor, rotation angle):
 *    - Run the "Move channels Tool Options" macro.
 *    - Enter the desired values for small/big step multipliers, scaling factor, and rotation angle.
 *    - Click `OK` to apply the settings.
 * 6. Save the modified image at any point by using standard ImageJ saving options.
 * 
 * Notes:
 * - The `small` and `big` step multipliers control the sensitivity of movement. `small` is for fine adjustments, while `big` is for coarse adjustments.
 * - Scaling factor affects the size of the channel. A factor of 1.0 means no scaling.
 * - Rotation angle is in degrees. A value of 0 means no rotation.
 * - Ensure that the image is properly aligned before applying large transformations.
 * 
 * Disclaimer:
 * Use this macro carefully as it performs transformations on your images. It's recommended to work on copies of your images to prevent accidental loss of data.
 */


/* Macro tool to move, scale, and rotate channels in multichannel images with sub-pixel resolution
 * Nicolas De Francesco - March 2020
 * Updated: September 2024
 */

var net_dx;
var net_dy;
var title;
var corrected="";
var temp;
var small = 30;
var big = 90;
var scaleFactor = 1.0;
var rotationAngle = 0;

macro "Setup [F5]" {
    title = getTitle();
    corrected = "corrected-"+title;
    temp = "temp-"+title;
    
    getDimensions(width, height, channels, slices, frames);
    
    net_dx=newArray(channels);
    net_dy=newArray(channels);

    if(!isOpen(corrected)) run("Duplicate...", "title=&corrected duplicate");
    moveChannel(1, 0, 0);
}

macro "Move channels Tool - Cf0f L18f8L818f Cfb8 O11ee O22cc" {
    shift=1;
    ctrl=2; 
    rightButton=4;
    alt=8;
    leftButton=16;
    insideROI = 32;
    getCursorLoc(x, y, z, flags);
    
    if(flags&leftButton!=0 && corrected==getTitle()){ 
        x2=x;
        y2=y;
        Stack.getPosition(channel, slice, frame);
        
        while (flags & leftButton != 0){
            getCursorLoc(x, y, z, flags);
            if (x!=x2 || y!=y2){
                dx = x - x2;
                dy = y - y2;
                mult = small;
                if(flags & ctrl == 0) mult = big;
                moveChannel(channel, dx/mult, dy/mult);
                wait(50);
                x2=x;
                y2=y;
            }
        }
    }
}

macro "Move channels Tool Options" {
    Dialog.create("Move Channels Options");
    Dialog.addMessage(
        "Usage:\n \n" +
        "Select the image to correct, and press F5 to create\n" +
        "a working copy (or to reset it). Select the move channel tool.\n \n" +
        "Select a channel to move in the copy, and click & drag.\n" +
        "Pressing Ctrl amplifies the mouse movement.\n" +
        "The zoom state of the image also changes the amount moved.\n \n" +
        "You can save the new image at any point.\n \n"
    );
    
    Dialog.addNumber("Small step multiplier:", small);
    Dialog.addNumber("Big step multiplier:", big);
    Dialog.addNumber("Scale factor:", scaleFactor);
    Dialog.addNumber("Rotation angle (degrees):", rotationAngle);
    Dialog.show();
    small = Dialog.getNumber();
    big = Dialog.getNumber();
    scaleFactor = Dialog.getNumber();
    rotationAngle = Dialog.getNumber();
}

function moveChannel(channel, ndx, ndy){
    setBatchMode(true);
    selectWindow(title);
    run("Duplicate...", "title=&temp duplicate channels=&channel");
    
    net_dx[channel-1] += ndx;
    net_dy[channel-1] += ndy;
    
    // Apply translation
    run("Translate...", "x="+net_dx[channel-1]+" y="+net_dy[channel-1]+" interpolation=Bicubic slice");
    
    // Apply scaling
    if (scaleFactor != 1.0) {
        run("Scale...", "x="+scaleFactor+" y="+scaleFactor+" interpolation=Bicubic");
    }
    
    // Apply rotation
    if (rotationAngle != 0) {
        run("Rotate...", "angle="+rotationAngle+" grid=1 interpolation=Bicubic");
    }
    
    run("Copy");
    close();
    
    selectWindow(corrected);
    Stack.setChannel(channel);
    run("Paste");
    run("Select None");
    setBatchMode(false);
}
