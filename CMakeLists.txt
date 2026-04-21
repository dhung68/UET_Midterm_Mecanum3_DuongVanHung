cmake_minimum_required(VERSION 3.8)
project(circle3)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch meshes urdf config rviz worlds
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/mecanum_kinematics.py
  scripts/odom_node.py
  scripts/arm_teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
