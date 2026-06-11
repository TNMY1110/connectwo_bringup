import rospy
from geometry_msgs.msg import Twist
import time

rospy.init_node('calib_test')
pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

msg = Twist()
msg.linear.x = 0.5

time.sleep(1)

start = time.time()
while time.time() - start < 2.0:
    pub.publish(msg)
    time.sleep(0.1)

msg.linear.x = 0.0
pub.publish(msg)
print("완료!")