# Agricultural Environment Workspace

## Project Status: 🚧 Work in Progress 🚧
**Note: This project is currently not finished and is under active development.**

This ROS Noetic workspace contains the simulation environment and core logic for an autonomous agricultural robot designed for precision weed targeting using computer vision.

### Demonstrations

**Image Processing Pipeline**  
<video src="image_processing_test.mov" width="600" controls></video>

**Laser Targeting Kinematics**  
<video src="laser_test.mov" width="600" controls></video>

### Packages
The workspace is divided into four main packages:
- **`virtual_farm_env`**: Procedurally generates the 3D Gazebo farm environments spanning different configurations of cotton, pumpkins, and weeds.
- **`ryobi_description`**: Contains the robot URDF chassis bounds and sensors (e.g., depth cameras, laser pointers).
- **`image_processing`**: Houses the YOLOv8 vision pipeline interpreting feeds to detect specific objects of interest.
- **`ryobi_control`**: The C++ logical core directing the robot to react to the coordinates parsed by the CV nodes.

Please refer to the `README.md` inside each respective package for more details on their specialized mechanics.
