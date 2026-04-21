#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import numpy as np

class MecanumMatrixNode(Node):
    def __init__(self):
        super().__init__('mecanum_kinematics_node')
        
        self.pub = self.create_publisher(Float64MultiArray, '/velocity_controller/commands', 10)
        
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.kinematics_callback, 10)

        self.R = 0.0485  # Bán kính bánh xe (m)
        self.L = 0.18    # Khoảng cách từ tâm đến bánh xe (m)
        self.beta = np.radians(45) # Góc con lăn
        self.alphas = np.radians([240, 120, 0]) # Góc đặt 3 bánh xe

        c1 = np.sin(self.alphas - self.beta)
        c2 = -np.cos(self.alphas - self.beta)
        c3 = np.full(3, self.L)

        self.H = (1.0 / (self.R * np.cos(self.beta))) * np.stack([c1, c2, c3], axis=1)
        
        self.get_logger().info("Ma Trận đã sẵn sàng!")

    def kinematics_callback(self, msg):
        V = np.array([msg.linear.x, msg.linear.y, msg.angular.z])

        wheel_velocities = self.H @ V

        out_msg = Float64MultiArray()
        out_msg.data = wheel_velocities.tolist()
        self.pub.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MecanumMatrixNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()