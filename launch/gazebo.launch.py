import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'circle3'
    pkg_share = get_package_share_directory(package_name)
    urdf_file = os.path.join(pkg_share, 'urdf', 'circle3.urdf')

    # 1. Thiết lập đường dẫn Mesh cho Gazebo
    install_dir = os.path.join(pkg_share, '..')
    set_gazebo_model_path = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', install_dir)

    # 2. Khai báo Robot State Publisher (Đọc URDF)
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    world_path = '/opt/ros/humble/share/turtlebot3_gazebo/worlds/turtlebot3_world.world' 

    # Giữ nguyên phần Include Gazebo bên dưới
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={'world': world_path}.items()
    )

    # 4. Spawn Robot vào Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'circle3_robot', 
                   '-x', '-2.0', '-y', '0.0', '-z', '0.3'],
        output='screen'
    )

    # 5. Các Controller Spawners (Dùng TimerAction để né lag cho máy Acer)
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"]
    )

    velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["velocity_controller"]
    )

    arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"]
    )

    # 6. Node RViz2 (Lấy cấu hình từ file display.launch.py của Hùng)
    # Lưu ý: Không cần joint_state_publisher_gui vì đã có Gazebo gửi joint states rồi
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'view_robot.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        # Dòng 62: Đảm bảo ở đây cũng dùng pkg_share (giống như hình bạn chụp)
        arguments=['-d', rviz_config_path] 
    )

    # Thêm đoạn này vào file gazebo.launch.py của bạn
    kinematics_node = Node(
        package='circle3',
        executable='mecanum_kinematics.py',
        output='screen'
    )

    # Trong file gazebo.launch.py
    odom_node = Node(
        package='circle3',
        executable='odom_node.py',
        output='screen'
    )
    # Thêm 'odom_node' vào danh sách trả về ở cuối file

    # Và nhớ thêm 'kinematics_node' vào trong phần return LaunchDescription([...])

   
    # Sắp xếp thứ tự chạy để tránh lỗi xung đột tài nguyên
    return LaunchDescription([
        set_gazebo_model_path,
        rsp,
        gazebo,
        spawn_entity,
        kinematics_node,
        odom_node,
        TimerAction(period=3.0, actions=[joint_state_broadcaster]),
        TimerAction(period=4.0, actions=[velocity_controller]),
        TimerAction(period=5.0, actions=[arm_controller]), # THÊM DÒNG NÀY VÀO ĐÂY
        TimerAction(period=6.0, actions=[rviz_node])
    ])