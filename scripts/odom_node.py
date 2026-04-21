#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Quaternion
import tf2_ros
import math
import numpy as np

class Circle3OdomNode(Node):
    def __init__(self):
        super().__init__('circle3_odom_node')
        
        # 1. Subscriber và Publisher
        self.subscription = self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # 2. Thông số Robot (Hùng kiểm tra lại theo URDF nhé)
        self.R = 0.0485  # Bán kính bánh xe (m)
        self.L = 0.18    # Khoảng cách từ tâm đến bánh xe (m)
        
        # 3. Trạng thái Robot
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.last_time = self.get_clock().now()

    def euler_to_quaternion(self, roll, pitch, yaw):
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        return qx, qy, qz, qw

    def joint_callback(self, msg):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        if dt <= 0: return

        # Lấy vận tốc góc 3 bánh xe (rad/s) từ Encoder ảo
        # Giả sử thứ tự: [sau_left, sau_right, truoc]
        try:
            w1, w2, w3 = msg.velocity[0], msg.velocity[1], msg.velocity[2]
        except IndexError: return

        # 4. Forward Kinematics cho robot 3 bánh (Mecanum/Omni 120 độ)
        # Tính vận tốc Robot trong hệ tọa độ của chính nó (Robot Frame)
        vx_robot = (self.R / 3.0) * (-math.sqrt(3)/2 * w1 + math.sqrt(3)/2 * w2)
        vy_robot = (self.R / 3.0) * (-0.5 * w1 - 0.5 * w2 + w3)
        vth = (self.R / (3.0 * self.L)) * (w1 + w2 + w3)

        # 5. Chuyển sang hệ tọa độ World (Odom Frame)
        delta_x = (vx_robot * math.cos(self.th) - vy_robot * math.sin(self.th)) * dt
        delta_y = (vx_robot * math.sin(self.th) + vy_robot * math.cos(self.th)) * dt
        delta_th = vth * dt

        self.x += delta_x
        self.y += delta_y
        self.th += delta_th

        # 6. Publish Odometry Message
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        qx, qy, qz, qw = self.euler_to_quaternion(0, 0, self.th)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        
        self.odom_pub.publish(odom)

        # 7. Publish TF (Để RViz khớp được odom và robot)
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

        self.last_time = current_time

def main(args=None):
    rclpy.init(args=args)
    node = Circle3OdomNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()