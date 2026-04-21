#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import sys, select, termios, tty

# Hướng dẫn điều khiển cho Hùng
msg = """
Điều khiển tay máy circle3 bằng bàn phím:
---------------------------
joint_slider (Tịnh tiến):   joint_2 (Xoay):
    w : Tăng (+)                a : Tăng (+)
    s : Giảm (-)                d : Giảm (-)

Space : Reset về 0
CTRL-C để thoát
"""

class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop')
        self.pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        
        self.slider_pos = 0.0
        self.joint2_pos = 0.0
        self.step_slider = 0.01 
        self.step_joint2 = 0.3 

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def send_cmd(self):
        traj = JointTrajectory()
        traj.joint_names = ['joint_slider', 'joint_2']
        p = JointTrajectoryPoint()
        p.positions = [float(self.slider_pos), float(self.joint2_pos)]
        p.time_from_start = Duration(sec=1, nanosec=500000000) # Phản hồi nhanh 0.5s
        traj.points.append(p)
        self.pub.publish(traj)

def main():
    rclpy.init()
    node = ArmTeleop()
    print(msg)
    try:
        while True:
            key = node.get_key()
            if key == 'w': node.slider_pos += node.step_slider
            elif key == 's': node.slider_pos -= node.step_slider
            elif key == 'a': node.joint2_pos += node.step_joint2
            elif key == 'd': node.joint2_pos -= node.step_joint2
            elif key == ' ': node.slider_pos, node.joint2_pos = 0.0, 0.0
            elif key == '\x03': break # CTRL-C
            
            if key in ['w','s','a','d',' ']:
                node.send_cmd()
                print(f"\rSlider: {node.slider_pos:.2f} | Joint2: {node.joint2_pos:.2f}", end="")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()