#include "ryobi_control/laser_targeter.h"
#include <cmath>

LaserTargeter::LaserTargeter(ros::NodeHandle& nh) : nh_(nh), current_state_(TargeterState::IDLE) {
    // Subscribe to weed list (list of Point32 inside a Polygon)
    weed_sub_ = nh_.subscribe("/weed_list", 10, &LaserTargeter::weedCallback, this);

    // Publishers for laser controllers and chassis
    pan_pub_ = nh_.advertise<std_msgs::Float64>("/ryobi/laser_pan_position_controller/command", 10);
    tilt_pub_ = nh_.advertise<std_msgs::Float64>("/ryobi/laser_tilt_position_controller/command", 10);
    cmd_vel_pub_ = nh_.advertise<geometry_msgs::Twist>("/cmd_vel", 10);

    ROS_INFO("Laser Targeter Node Initialized in IDLE state.");
}

void LaserTargeter::weedCallback(const geometry_msgs::Polygon::ConstPtr& msg) {
    // Only update the list of plants when IDLE. 
    // While targeting, we ignore new detections so we process the current batch cleanly.
    if (current_state_ == TargeterState::IDLE) {
        latest_weeds_ = *msg;
    }
}

void LaserTargeter::startTargeting() {
    if (current_state_ == TargeterState::TARGETING) {
        ROS_WARN("Already in TARGETING state. Ignoring call.");
        return;
    }

    current_state_ = TargeterState::TARGETING;
    ROS_INFO("State changed to TARGETING. Starting step-by-step execution.");

    // 1. Brake the robot
    geometry_msgs::Twist stop_msg;
    stop_msg.linear.x = 0; stop_msg.linear.y = 0; stop_msg.linear.z = 0;
    stop_msg.angular.x = 0; stop_msg.angular.y = 0; stop_msg.angular.z = 0;
    cmd_vel_pub_.publish(stop_msg);
    ROS_INFO("Robot braked. Velocity set to 0.");

    // 2. We use the latest_weeds_ we saved
    if (latest_weeds_.points.empty()) {
        ROS_INFO("No weeds in the current list. Returning to IDLE.");
        current_state_ = TargeterState::IDLE;
        return;
    }

    ROS_INFO("Found %zu weeds in the list. Targeting them one by one.", latest_weeds_.points.size());

    // 3. Iterate through weeds with 4 second delay
    for (size_t i = 0; i < latest_weeds_.points.size(); ++i) {
        auto& pt = latest_weeds_.points[i];
        
        double x_g = pt.x;
        double y_g = pt.y;
        double z_g = pt.z;

        // Kinematic translation variables based on URDF offsets
        // Ground point directly below camera is at X=0.5, Z=-0.175 (relative to base_chassis)
        double x_weed = 0.5 + x_g;
        double y_weed = 0.0 + y_g;
        double z_weed = -0.175 + z_g;

        // Laser pan joint is at X=0.47, Z=0.30, but tilt joint is Z=0.02 above it.
        // Therefore, the true physical pivot of the tilt mechanism is Z=0.32.
        double x_rel = x_weed - 0.47;
        double y_rel = y_weed - 0.0;
        double z_rel = z_weed - 0.32;

        // Calculate Pan Angle (Rotation around Z)
        double pan_angle = std::atan2(y_rel, x_rel);

        // Calculate Tilt Angle (Rotation around Y)
        // The red beam is visually offset by Z=0.03 from the tilt joint (relative to laser_tilt_link).
        // To aim an offset beam, we rigorously solve: z_rel * cos(tilt) + l_xy * sin(tilt) = 0.03
        double l_xy = std::sqrt(x_rel*x_rel + y_rel*y_rel);
        
        double A = z_rel;
        double B = l_xy;
        double C = 0.03; // Z-axis offset of the red beam inside the URDF
        
        double R = std::sqrt(A*A + B*B);
        // Ensure we don't try to take asin of a value > 1 if the target is physically inside the offset radius
        double tilt_angle = 0.0;
        if (std::abs(C / R) <= 1.0) {
            double phi = std::atan2(A, B);
            tilt_angle = std::asin(C / R) - phi;
        }

        // Publish commands
        std_msgs::Float64 pan_cmd, tilt_cmd;
        pan_cmd.data = pan_angle;
        tilt_cmd.data = tilt_angle;
        
        pan_pub_.publish(pan_cmd);
        tilt_pub_.publish(tilt_cmd);

        ROS_INFO("Targeting weed %zu/%zu at (%.2f, %.2f, %.2f) -> Pan: %.2f rad, Tilt: %.2f rad",
                 i+1, latest_weeds_.points.size(), x_g, y_g, z_g, pan_angle, tilt_angle);

        // Wait 4 seconds for the laser to stay targeted
        ros::Duration(4.0).sleep();
    }

    ROS_INFO("Finished targeting sequence. Returning to IDLE.");
    current_state_ = TargeterState::IDLE;
}
