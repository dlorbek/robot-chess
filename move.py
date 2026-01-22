#!/usr/bin/env python

import rospy
from sensor_msgs.msg import JointState
import moveit_commander
import pickle
import tf2_ros
from geometry_msgs.msg import Pose
import numpy as np
from gripper import Gripper


class MoveCommander:
    
    def __init__(self):
        

        self.JOINT_NAMES = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

        self.HOME_JOINTS = [0.0, -1.57, -1.57, 0, 0.0, 0.0]
        rospy.init_node('moveit_programmer')
        self.moveit_interface = moveit_commander.MoveGroupCommander('panda_arm')
        
        self.init_joints = JointState()
        self.init_joints.header.stamp = rospy.Time.now()
        self.init_joints.name = self.JOINT_NAMES
        self.init_joints.position = self.HOME_JOINTS
        
        tf_buffer = tf2_ros.Buffer()
        tf_listener = tf2_ros.TransformListener(tf_buffer)

        rospy.sleep(0.5)

        current_transform = tf_buffer.lookup_transform(
            'panda_link0',
            'panda_link7',
            rospy.Time(0)
        )
        
        self.tf_broadcaster = tf2_ros.StaticTransformBroadcaster()
        
        

    def moveL(self, path, eef_step = 0.01, jump_threshold = 0):
        (plan1, fraction) = self.moveit_interface.compute_cartesian_path(
                                    path,   # waypoints to follow
                                    eef_step,        # eef_step
                                    jump_threshold)         # jump_threshold

        self.moveit_interface.execute(plan1, wait=True)

    def moveJ(self, goal):
        self.moveit_interface.go(goal, wait=True)

    def calibrate_chessboard(self):
        poses = []
        for i in range(3):
            raw_input("Set in position:")
            poses.append( self.moveit_interface.get_current_pose() )

        with open('chessboard_config.pickle', 'wb') as file:
            pickle.dump(poses, file)
    
    def calibrate_home(self):
        raw_input("Set in position:")
        home =  self.moveit_interface.get_current_pose()
        with open('home_config.pickle', 'wb') as file:
            pickle.dump(home, file)

    def get_chessboard(self, T1, T2, T3):

        A1H1 = np.array(T2) - np.array(T1)
        H1H8 = np.array(T3) - np.array(T2)
        chessbord = {}

        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        for i,f in enumerate(files):
            for r in ranks:
                chessbord[f+r] = np.array(T1) + A1H1/7*i + H1H8/7*(int(r)-1)

        return chessbord

    def offset(self, pose, x, y, z):
        pose1 = Pose()
        pose1.position.x = pose.position.x + x
        pose1.position.y = pose.position.y + y
        pose1.position.z = pose.position.z + z
        pose1.orientation.x = pose.orientation.x
        pose1.orientation.y = pose.orientation.y
        pose1.orientation.z = pose.orientation.z
        pose1.orientation.w = pose.orientation.w
        return pose1

    def move_piece(self, square1, square2):
        self.moveJ(self.offset(square1, 0, 0, 0.1))
        self.moveL([square1])
        
        #gripper close
        print("Closing gripper")
            
        self.moveL([self.offset(square1, 0, 0, 0.1), self.offset(square2, 0, 0, 0.1), square2])
        print("Opening gripper")
        self.moveL([self.offset(square2, 0, 0, 0.2)])
        
        
        #self.moveJ(home)


    def chessboard(self, p1, p2, p3):
        pose1 = p1.pose
        pose2 = p2.pose
        pose3 = p3.pose

        T1 = [pose1.position.x, pose1.position.y, pose1.position.z]
        T2 = [pose2.position.x, pose2.position.y, pose2.position.z]
        T3 = [pose3.position.x, pose3.position.y, pose3.position.z]

        board = self.get_chessboard(T1, T2, T3)

        chessboard = {}

        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        for f in files:
            for r in ranks:
                chessboard[f+r] = Pose()
                chessboard[f+r].position.x = board[f+r][0]
                chessboard[f+r].position.y = board[f+r][1]
                chessboard[f+r].position.z = board[f+r][2]

                chessboard[f+r].orientation = pose1.orientation

        return chessboard



if __name__ == '__main__':
    rospy.init_node('moveit_programmer')

    joint_pub = rospy.Publisher('/move_group/fake_controller_joint_states', JointState, queue_size=10)
    rospy.sleep(0.1)
    tf_broadcaster = tf2_ros.StaticTransformBroadcaster()

    init_joints = JointState()
    init_joints.header.stamp = rospy.Time.now()
    init_joints.name = JOINT_NAMES
    init_joints.position = HOME_JOINTS
    joint_pub.publish(init_joints)

    moveit_interface = moveit_commander.MoveGroupCommander('panda_arm')

    pose = moveit_interface.get_current_pose()
    
    rospy.loginfo(pose)
    
    tf_buffer = tf2_ros.Buffer()
    tf_listener = tf2_ros.TransformListener(tf_buffer)

    rospy.sleep(0.5)

    current_transform = tf_buffer.lookup_transform(
        'panda_link0',
        'panda_link7',
        rospy.Time(0)
    )
    
    raw_input("Press Enter")

    pose_goal = Pose(
       position=current_transform.transform.translation, orientation=current_transform.transform.rotation)
    pose_goal.position.z += 0.1
    
    with open('chessboard_config.pickle', 'rb') as file:
    # Load the object from the file
        loaded_data = pickle.load(file)
    
    bord = chessboard(loaded_data[0], loaded_data[1], loaded_data[2])
    moveit_interface.go(bord['h8'], wait=True)