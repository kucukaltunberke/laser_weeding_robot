#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, Point32, Polygon
from cv_bridge import CvBridge, CvBridgeError
from ultralytics import YOLO

class WeedDetector:
    def __init__(self):
        # 1. Initialize the ROS node
        rospy.init_node('weed_detector_yolo', anonymous=True)

        # 2. Load your custom trained model
        import rospkg, os
        model_path = os.path.join(rospkg.RosPack().get_path('image_processing'), 'weight', 'best.pt')
        self.model = YOLO(model_path)

        # 3. Initialize the ROS-to-OpenCV bridge
        self.bridge = CvBridge()

        # 4. Use message_filters to synchronize RGB and Depth images
        import message_filters
        self.rgb_sub = message_filters.Subscriber("/camera1/image_raw", Image)
        self.depth_sub = message_filters.Subscriber("/camera1/depth/image_raw", Image)
        
        self.ts = message_filters.ApproximateTimeSynchronizer([self.rgb_sub, self.depth_sub], queue_size=10, slop=0.1)
        self.ts.registerCallback(self.image_callback)

        import sys, os, rospkg
        script_path = os.path.join(rospkg.RosPack().get_path('image_processing'), 'scripts')
        sys.path.append(script_path)
        from weed_coordinate_solver import WeedCoordinateSolver
        self.coordinate_solver = WeedCoordinateSolver()

        # Optional: Publisher to view the live YOLO annotations in RViz or rqt_image_view
        self.image_pub = rospy.Publisher("/yolo/annotated_image", Image, queue_size=1)
        self.weed_list_pub = rospy.Publisher("/weed_list", Polygon, queue_size=10)

    def image_callback(self, rgb_data, depth_data):
        try:
            # 5. Convert the incoming ROS Image message directly into an OpenCV image (NumPy array)
            cv_image = self.bridge.imgmsg_to_cv2(rgb_data, "bgr8")
            cv_depth = self.bridge.imgmsg_to_cv2(depth_data, "32FC1")
        except CvBridgeError as e:
            rospy.logerr(f"CvBridge Error: {e}")
            return

        # 6. Run inference directly on the RAM-stored image array (Notice save=False)
        results = self.model.predict(source=cv_image, imgsz=1080, conf=0.25, save=False, verbose=False)

        import cv2
        annotated_frame = cv_image.copy()
        
        weed_polygon = Polygon()

        # 7. Extract the pixel coordinates for your inverse kinematics
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get the bounding box corner coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # Calculate the exact center pixel (u, v) of the weed
                u = int((x1 + x2) / 2)
                v = int((y1 + y2) / 2)
                
                confidence = float(box.conf[0].cpu().numpy())
                
                # Fetch metric distance from depth camera
                depth_val = cv_depth[v, u]
                coords_3d = self.coordinate_solver.get_3d_coordinate(u, v, depth_val)
                
                if coords_3d:
                    x_g, y_g, z_g = coords_3d
                    rospy.loginfo(f"Weed at pixel ({u}, {v}) | Confidence: {confidence:.2f} | 3D Ground: X={x_g:.2f}m, Y={y_g:.2f}m, Z={z_g:.2f}m")
                    
                    p = Point32()
                    p.x = x_g
                    p.y = y_g
                    p.z = z_g
                    weed_polygon.points.append(p)
                else:
                    rospy.loginfo(f"Weed at pixel ({u}, {v}) | Confidence: {confidence:.2f} | 3D: Invalid depth")
                
                # Draw a green bounding box (BGR: 0, 255, 0)
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
                
                # Draw a small red dot at the center coordinates
                cv2.circle(annotated_frame, (u, v), 5, (0, 0, 255), -1)
                
                # Write the confidence near the box
                label = f"Weed {confidence:.2f}"
                cv2.putText(annotated_frame, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Convert the manually annotated image back to a ROS message to publish
            try:
                ros_img = self.bridge.cv2_to_imgmsg(annotated_frame, "bgr8")
                self.image_pub.publish(ros_img)
            except CvBridgeError as e:
                rospy.logerr(f"CvBridge Publish Error: {e}")
                
        self.weed_list_pub.publish(weed_polygon)

if __name__ == '__main__':
    try:
        detector = WeedDetector()
        rospy.loginfo("YOLOv8 Weed Detection Node Started. Waiting for images...")
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
