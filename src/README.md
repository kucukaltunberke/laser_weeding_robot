# Agricultural Environment Workspace

## Project Status: 🚧 Work in Progress 🚧
**Note: This project is currently not finished and is under active development.**

This ROS Noetic workspace contains the simulation environment and core logic for an autonomous agricultural robot designed for precision weed targeting using computer vision.

### Demonstrations

**Image Processing Pipeline**  
https://github.com/kucukaltunberke/laser_weeding_robot/raw/main/src/image_processing_test.mp4

**Laser Targeting Kinematics**  
https://github.com/kucukaltunberke/laser_weeding_robot/raw/main/src/laser_test.mp4

### Packages
The workspace is divided into four main packages, all optimized for the **`ryobi`** robot platform:
- **`virtual_farm_env`**: Procedurally generates the 3D Gazebo farm environments spanning different configurations of cotton, pumpkins, and weeds.
- **`ryobi_description`**: Contains the robot URDF chassis bounds and sensors (e.g., depth cameras, laser pointers) for the **`ryobi`** robot.
- **`image_processing`**: Houses the YOLOv8 vision pipeline interpreting feeds to detect specific objects of interest.
- **`ryobi_control`**: The C++ logical core directing the **`ryobi`** robot to react to the coordinates parsed by the CV nodes.

Please refer to the `README.md` inside each respective package for more details on their specialized mechanics.
