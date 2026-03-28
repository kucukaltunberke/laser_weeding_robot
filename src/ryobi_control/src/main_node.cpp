#include <ros/ros.h>
#include "ryobi_control/laser_targeter.h"

int main(int argc, char** argv) {
    ros::init(argc, argv, "laser_targeter");
    ros::NodeHandle nh;

    LaserTargeter targeter(nh);

    // Using AsyncSpinner because we use ros::Duration::sleep in the targeter,
    // and if we used a standard single-threaded spin, we might block callbacks.
    // Though we intentionally ignore weeds while targeting, AsyncSpinner is 
    // good practice when blocking operations exist in case we need other callbacks.
    ros::AsyncSpinner spinner(2);
    spinner.start();

    // Sleep a bit on start to let subscribers connect and the camera to publish a frame
    ROS_INFO("Waiting 5 seconds for initial weed detections...");
    ros::Duration(5.0).sleep();

    // Example sequence: The user wanted it to activate and target step-by-step
    // For now, we just call it once. You can also hook this to a service or subscriber.
    targeter.startTargeting();

    // Keep node alive if we want to call it again or debug
    ros::waitForShutdown();
    
    return 0;
}
