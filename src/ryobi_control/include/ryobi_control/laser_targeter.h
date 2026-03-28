#ifndef LASER_TARGETER_H
#define LASER_TARGETER_H

#include <ros/ros.h>
#include <geometry_msgs/Polygon.h>
#include <geometry_msgs/Point32.h>
#include <std_msgs/Float64.h>
#include <geometry_msgs/Twist.h>
#include <vector>

enum class TargeterState {
    IDLE,
    TARGETING
};

class LaserTargeter {
private:
    ros::NodeHandle nh_;
    ros::Subscriber weed_sub_;
    ros::Publisher pan_pub_;
    ros::Publisher tilt_pub_;
    ros::Publisher cmd_vel_pub_;

    geometry_msgs::Polygon latest_weeds_;
    TargeterState current_state_;

    void weedCallback(const geometry_msgs::Polygon::ConstPtr& msg);

public:
    LaserTargeter(ros::NodeHandle& nh);
    void startTargeting();
};

#endif // LASER_TARGETER_H
