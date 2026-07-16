#!/bin/bash

source /opt/ros/humble/setup.bash
source /root/Grupo2-S004/install/setup.bash 2>/dev/null || true

export ROS_DOMAIN_ID=20
export ROS_LOCALHOST_ONLY=0

echo "====================================="
echo "  PARADA DE EMERGENCIA DEL ROBOT"
echo "  linear.x = 0"
echo "  angular.z = 0"
echo "====================================="

ros2 topic pub \
  --rate 20 \
  --times 60 \
  /cmd_vel \
  geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

echo ""
echo "ROBOT DETENIDO."
