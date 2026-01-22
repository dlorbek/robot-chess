#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Pose
from franka_gripper.msg import MoveAction, MoveGoal
import actionlib


class Gripper:
    
    def __init__(self):
        rospy.init_node('franka_test_gripper', anonymous=True)
        self.gripper_client = actionlib.SimpleActionClient('/franka_gripper/move', MoveAction)
    
        self.gripper_client.wait_for_server()
        print("server active")
    

    def set_gripper(self, state):
        # state: 1 - close, 0 - open
        goal = MoveGoal() #define action goal msg
        if state > 0:
            # close gripper to predfined position
            close_dist = 0.0025 # gripper width at the end of the move
            close_speed = 0.05
            goal.width = close_dist
            goal.speed = close_speed
        else:
            # open gripper to predfined position
            open_dist = 0.1 # gripper width at the end of the move
            open_speed = 0.05
            goal.width = open_dist
            goal.speed = open_speed
        # send goal 
        self.gripper_client.send_goal(goal)


def offset(pose, x, y, z):
    pose1 = pose
    pose1.position.x += x
    pose1.position.y += y
    pose1.position.z += z
    return pose1
    

# definicija globalnih spremenljivk

#move = VR_franka()




# definicija funkcije ob prejetem sporocilu na serverju
def callback_number(msg):
    print(msg)


if __name__ == '__main__':
    grip = gripper()
    # definicija subscriberja
    #sub = rospy.Subscriber('/franka_lr_state/pose', Pose, callback_number)
    #rospy.sleep(0.5)
    grip.set_gripper(1)
    # rospy.sleep(3)
    # grip.set_gripper(0)
    
    #rospy.spin()