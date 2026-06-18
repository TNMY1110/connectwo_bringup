#!/usr/bin/env python3
import rospy
import math
from sensor_msgs.msg import LaserScan

# 지지대가 가리는 각도 범위 (라디안). 실제 측정해서 조정 필요
BLOCKED_RANGES = [
    (math.radians(83), math.radians(98)),    # 왼쪽 지지대
    (math.radians(-98), math.radians(-83)),  # 오른쪽 지지대
]

def scan_callback(msg):
    new_msg = msg
    ranges = list(msg.ranges)
    angle = msg.angle_min
    for i in range(len(ranges)):
        for (low, high) in BLOCKED_RANGES:
            if low <= angle <= high:
                ranges[i] = float('inf')  # 해당 구간 무효화
                break
        angle += msg.angle_increment
    new_msg.ranges = ranges
    pub.publish(new_msg)

if __name__ == '__main__':
    rospy.init_node('lidar_blind_spot_filter')
    pub = rospy.Publisher('/scan_filtered', LaserScan, queue_size=10)
    rospy.Subscriber('/scan', LaserScan, scan_callback)
    rospy.spin()