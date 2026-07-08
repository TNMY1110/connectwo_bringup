#!/usr/bin/env python3
import rospy
import time
import copy
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped, PoseStamped
from actionlib_msgs.msg import GoalStatusArray

class NavigationManager:
    def __init__(self):
        rospy.init_node('navigation_manager_node')
        
        # 기본 변수 설정
        self.is_moving = False
        self.last_stop_time = rospy.Time.now()
        self.localization_triggered = True
        self.current_pose = None
        
        self.last_goal = None
        self.retry_count = 0
        self.max_retries = 3          # 최대 재시도 횟수
        self.retry_delay = 5.0        # 에러 발생 후 재시도까지 대기 시간 (5초)
        self.is_aborted = False

        # 구독자(Subscribers)
        rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)
        rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.pose_callback)
        rospy.Subscriber('/move_base/status', GoalStatusArray, self.status_callback)
        rospy.Subscriber('/move_base/current_goal', PoseStamped, self.goal_callback)

        # 발행자(Publishers)
        self.initial_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=1)
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=1)

    def cmd_vel_callback(self, msg):
        if abs(msg.linear.x) > 0.005 or abs(msg.angular.z) > 0.005:
            self.is_moving = True
            self.localization_triggered = False
        else:
            if self.is_moving:
                self.is_moving = False
                self.last_stop_time = rospy.Time.now()

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, msg):
        # 유저가 새로 내린 목적지를 기억해둡니다 (재시도용)
        # 본인이 재발행한 골은 무시하기 위해 타임스탬프 차이를 둡니다.
        if self.last_goal is None or (msg.header.stamp - self.last_goal.header.stamp).to_sec() > 1.0:
            self.last_goal = msg
            self.retry_count = 0 # 새 목적지가 오면 재시도 카운트 리셋

    def status_callback(self, msg):
        if not msg.status_list:
            return
        
        # 가장 최근의 move_base 상태 확인
        last_status = msg.status_list[-1].status
        
        # Status 4 = ABORTED (경로 찾기 실패 및 포기 상태)
        if last_status == 4:
            if not self.is_aborted:
                self.is_aborted = True
                self.handle_abort()
        else:
            self.is_aborted = False

    def handle_abort(self):
        if self.last_goal and self.retry_count < self.max_retries:
            self.retry_count += 1
            rospy.logwarn(f" [경고] move_base가 주행을 포기했습니다. {self.retry_delay}초 후 다시 시도합니다... (재시도: {self.retry_count}/{self.max_retries})")
            
            # 지정한 시간(초)만큼 대기
            rospy.Timer(rospy.Duration(self.retry_delay), self.retry_goal, oneshot=True)

        else:
            if self.retry_count >= self.max_retries:
                rospy.logerr("최대 재시도 횟수를 초과하여 주행 복구를 중단합니다.")
                self.is_aborted = False

    def retry_goal(self, event):
        self.is_aborted = False

        if self.last_goal:
            self.last_goal.header.stamp = rospy.Time.now()
            self.goal_pub.publish(self.last_goal)

    def spin(self):
        rate = rospy.Rate(5) # 5Hz
        while not rospy.is_shutdown():
            # [기존 기능] 정지 시 AMCL 위치 및 회전 정렬 보정
            if not self.is_moving and not self.localization_triggered and self.current_pose and not self.is_aborted:
                if (rospy.Time.now() - self.last_stop_time).to_sec() > 1.5:
                    rospy.loginfo("로봇 정지 감지: AMCL 위치 및 회전 정렬 트리거를 발행합니다.")
                    stop_pose = copy.deepcopy(self.current_pose)
                    stop_pose.pose.covariance = [
                        0.15, 0, 0, 0, 0, 0,
                        0, 0.15, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0.25
                    ]
                    self.initial_pose_pub.publish(stop_pose)
                    self.localization_triggered = True
            rate.sleep()

if __name__ == '__main__':
    try:
        manager = NavigationManager()
        manager.spin()
    except rospy.ROSInterruptException:
        pass