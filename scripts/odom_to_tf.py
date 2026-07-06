#!/usr/bin/env python3
import rospy
import tf
from nav_msgs.msg import Odometry

# 전역 변수로 최신 오도메트리 데이터를 보관할 객체 선언
current_odom = None
def odom_callback(msg):
    global current_odom
    current_odom = msg # 최신 메시지가 들어오면 전역 변수에 계속 업데이트

def shutdown_hook():
    rospy.loginfo("odom_to_tf_converter shutting down...")

if __name__ == '__main__':
    rospy.init_node('odom_to_tf_converter')
    
    # TransformBroadcaster는 루프 외부에서 한 번만 생성
    br = tf.TransformBroadcaster()
    
    # /odom 토픽 구독
    rospy.Subscriber('/odom', Odometry, odom_callback)
    
    # TF 발행 주기를 50Hz(0.02초)로 고정하여 라이다 속도와 동기화
    rate = rospy.Rate(50) 
    
    rospy.loginfo("odom_to_tf_converter node started with 50Hz Rate.")
    
    while not rospy.is_shutdown():
        # 최초 데이터가 들어오기 전까지는 대기
        if current_odom is not None:
            pos = current_odom.pose.pose.position
            ori = current_odom.pose.pose.orientation
            
            # 타임스탬프 동기화
            current_time = rospy.Time.now()
            
            br.sendTransform(
                (pos.x, pos.y, pos.z),
                (ori.x, ori.y, ori.z, ori.w),
                current_time, # 현재 시간 주입!
                "base_footprint",
                "odom"
            )
            
        rate.sleep()