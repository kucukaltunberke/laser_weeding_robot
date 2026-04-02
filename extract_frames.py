#!/usr/bin/env python3
import rosbag
import cv2
from cv_bridge import CvBridge

bag = rosbag.Bag('targeting_video.bag')
bridge = CvBridge()
count = 0

for topic, msg, t in bag.read_messages(topics=['/yolo/annotated_image']):
    cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    cv2.imwrite('/tmp/yolo_frames/frame%04d.jpg' % count, cv_img)
    count += 1

bag.close()
print("Saved %d frames" % count)
