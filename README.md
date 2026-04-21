# Robot Circle3 - Đồ án Giữa kỳ Robotics UET

## 1. Cấu trúc Package
* `config/`: Chứa file `controllers.yaml` cấu hình cho bánh xe và tay máy.
* `launch/`: File `gazebo.launch.py` tích hợp khởi chạy Gazebo, RViz và các controller.
* `meshes/`: Chứa các file thiết kế `.STL` xuất từ SolidWorks.
* `urdf/`: File mô tả vật lý robot sử dụng Xacro để quản lý link động.
* `scripts/`: Các node Python xử lý động học và điều khiển bàn phím.
* `rviz/`: File cấu hình giao diện RViz `.rviz` đã lưu sẵn các topic cảm biến.

## 2. Các thư viện cần thiết
Trước khi chạy, hãy đảm bảo máy tính đã cài đặt đầy đủ các gói hỗ trợ sau:
* sudo apt update
* sudo apt install ros-humble-xacro \
                 ros-humble-gazebo-ros2-control \
                 ros-humble-teleop-twist-keyboard \
                 ros-humble-joint-state-publisher-gui
## 3. Hướng dẫn cài đặt
* mkdir -p ~/rosgk_ws/src
* cd ~/rosgk_ws/src
* git clone https://github.com/dhung68/UET_Midterm_Mecanum3_DuongVanHung.git
* cd ~/rosgk_ws
* colcon build --symlink-install --packages-select circle3
* source install/setup.bash
  
## 4. Khởi chạy mô phỏng
* ros2 launch circle3 gazebo.launch.py
* ros2 run teleop_twist_keyboard teleop_twist_keyboard
* ros2 run circle3 arm_teleop.py
