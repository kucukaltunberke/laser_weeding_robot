#include <ros/ros.h>
#include "ryobi_control/laser_targeter.h"

int main(int argc, char** argv) {
    ros::init(argc, argv, "laser_targeter");
    ros::NodeHandle nh;

    LaserTargeter targeter(nh);

    ros::AsyncSpinner spinner(2);
    spinner.start();

    // Sleep a bit on start to let subscribers connect and the camera to publish a frame
    ROS_INFO("Waiting 5 seconds for initial weed detections...");
    ros::Duration(5.0).sleep();

    // For now, we just call it once. You can also hook this to a service or subscriber.
    targeter.startTargeting();

    // Keep node alive if we want to call it again or debug
    ros::waitForShutdown();
    
    return 0;
}
