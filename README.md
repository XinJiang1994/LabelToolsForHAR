# LabelToolsForHAR

# Installation

## For Linux

  sudo apt install python-tk

  pip3 install tk

  pip3 install opencv-python

  pip3 install "opencv-python-headless<4.3"


## For Mac

  brew install python-tk

  pip3 install tk

  pip3 install opencv-python

  pip3 install "opencv-python-headless<4.3"
  
# Usage

1. [Copy this script to the data root, then run "python LabelTool.py"]【Optional】

2. Select the class you want to label

3. Select the video path you want to label

4. Click start labeling button

5. If current frame belongs to the class you choose, press 1. Else press 0.

   press '<--' key to view previous frame, '-->' key to the next frame.

6. Press q to finish labeling of current video.

# Results 

The label files are saved in the video root folder, 

for example [video_root...]/2022-06-23_20-00-00/labels/

# hints

You can press the following button to set speed:

d: x2

t: x10

h: x100

