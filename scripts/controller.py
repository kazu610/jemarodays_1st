#! /usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf import transformations
from std_srvs.srv import *

import math

active_ = False

pub_ = None
regions_ = {
    'right': 0,
    'fright': 0,
    'front': 0,
    'fleft': 0,
    'left': 0,
}
state_ = 0
state_dict_ = {
    0: 'find the wall',
    1: 'turn left',
    2: 'follow the wall',
}

'''
def wall_follower_switch(req): # service server
    global active_
    active_ = req.data
    res = SetBoolResponse()
    res.success = True
    res.message = 'Done!'
    return res
'''


def clbk_laser(msg): # callback of laserscaner
    range_front = msg.ranges[0:72] + msg.ranges[648:720]
    global regions_
    regions_ = {
        'right':  min(min(msg.ranges[450:504]), 10),
        'fright': min(min(msg.ranges[504:648]), 10),
        'front':  min(min(range_front), 10),
        'fleft':  min(min(msg.ranges[72:216]), 10),
        'left':   min(min(msg.ranges[216:270]), 10),
    }

    take_action()
    rospy.loginfo(regions_['front'])


def change_state(state):
    global state_, state_dict_
    if state is not state_:
        print ('Wall follower - [%s] - %s' % (state, state_dict_[state]))
        state_ = state


def take_action(): # called by clbk_laser
    global regions_
    regions = regions_
    msg = Twist()
    linear_x = 0
    angular_z = 0
    state_description = ''

    d0 = 0.5 # for front
    d = 0.6 # for other regions

    if regions['front'] > d0 and regions['fleft'] > d and regions['fright'] > d:
        state_description = 'case 1 - nothing'
        change_state(0)
    elif regions['front'] < d0 and regions['fleft'] > d and regions['fright'] > d:
        state_description = 'case 2 - front'
        change_state(1)
    elif regions['front'] > d0 and regions['fleft'] > d and regions['fright'] < d:
        state_description = 'case 3 - fright'
        change_state(2)
    elif regions['front'] > d0 and regions['fleft'] < d and regions['fright'] > d:
        state_description = 'case 4 - fleft'
        change_state(0)
    elif regions['front'] < d0 and regions['fleft'] > d and regions['fright'] < d:
        state_description = 'case 5 - front and fright'
        change_state(1)
    elif regions['front'] < d0 and regions['fleft'] < d and regions['fright'] > d:
        state_description = 'case 6 - front and fleft'
        change_state(1)
    elif regions['front'] < d0 and regions['fleft'] < d and regions['fright'] < d:
        state_description = 'case 7 - front and fleft and fright'
        change_state(1)
    elif regions['front'] > d0 and regions['fleft'] < d and regions['fright'] < d:
        state_description = 'case 8 - fleft and fright'
        change_state(0)
    else:
        state_description = 'unknown case'
        rospy.loginfo(regions)


def find_wall(): # implement PD control? could be integrated with follow the wall
    msg = Twist()
    msg.linear.x = 0.2
    msg.angular.z = -0.3
    return msg


def turn_left(): # if syntax for clockwise and anticlockwise + msg.linear.x
    msg = Twist()
    msg.angular.z = 0.3
    return msg


def follow_the_wall():
    global regions_

    msg = Twist()
    msg.linear.x = 0.5
    return msg


def main():
    global pub_, active_

    rospy.init_node('reading_laser')

    pub_ = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    sub = rospy.Subscriber('/scan', LaserScan, clbk_laser)

    # srv = rospy.Service('wall_follower_switch', SetBool, wall_follower_switch)

    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        '''
        if not active_:
            rate.sleep()
            continue
        else:
            msg = Twist()
            if state_ == 0:
                msg = find_wall() # important I guess
            elif state_ == 1:
                msg = turn_left()
            elif state_ == 2:
                msg = follow_the_wall()
            else:
                rospy.logerr('Unknown state!')

            pub_.publish(msg)

        rate.sleep()
        '''

        msg = Twist()
        if state_ == 0:
            msg = find_wall() # important I guess
        elif state_ == 1:
            msg = turn_left()
        elif state_ == 2:
            msg = follow_the_wall()
        else:
            rospy.logerr('Unknown state!')

        pub_.publish(msg)

        rate.sleep()


if __name__ == '__main__':
    main()
