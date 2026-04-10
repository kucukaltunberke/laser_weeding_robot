# image_processing


This package is dedicated to running image processing algorithms for agricultural analysis. It utilizes a trained YOLOv8 model subscribing to raw camera images emitted from Gazebo to identify models such as weeds vs. crop variants. 

### Demonstration
<video src="https://github.com/kucukaltunberke/laser_weeding_robot/raw/main/src/image_processing_test.mov" width="600" controls></video>

> [!NOTE]
> **Future Improvements**: Further improvement on the `image_processing` package is going to be focused heavily on **filtering**. Developing logical stability sweeps over frame-to-frame bounding boxes will guarantee smoother inputs for downstream kinematics.

