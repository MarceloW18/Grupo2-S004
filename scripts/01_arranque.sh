#!/bin/bash

source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=20
source /root/Grupo2-S004/install/setup.bash

cd /root/Grupo2-S004

echo "======================================"
echo " RC0 - PARTE A - ARRANQUE"
echo " Grupo 2 - S-004"
echo " ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "======================================"

ros2 launch capytown_esan bringup.launch.py &
LAUNCH_PID=$!

sleep 4

{
    echo "RC0 - Grupo 2 - S-004"
    echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
    echo ""
    echo "===== NODOS ====="
    ros2 node list

    echo ""
    echo "===== TOPICS ====="
    ros2 topic list

    echo ""
    echo "===== FRECUENCIA /odom ====="
    timeout 6 ros2 topic hz /odom || true

    echo ""
    echo "===== FRECUENCIA /imu ====="
    timeout 6 ros2 topic hz /imu || true

} | tee setup_log.txt

echo ""
echo "ARRANQUE LISTO."
echo "Deja esta terminal abierta."
echo "Para terminar: Ctrl+C"

wait $LAUNCH_PID
