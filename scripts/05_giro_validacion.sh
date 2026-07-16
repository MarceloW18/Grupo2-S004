#!/bin/bash

source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=20
source /root/Grupo2-S004/install/setup.bash

cd /root/Grupo2-S004

BEFF=$1

if [ -z "$BEFF" ]; then
    echo "Uso:"
    echo "./scripts/05_giro_validacion.sh <b_eff_final>"
    exit 1
fi

if [ -e "bags/rc0_val_giro" ]; then
    echo "ERROR: bags/rc0_val_giro ya existe."
    exit 1
fi

echo "======================================"
echo " VALIDACION A4 - GIRO 360"
echo " b_eff FINAL = $BEFF"
echo " NO RECALIBRAR"
echo "======================================"

read -p "Coloca el robot en G y presiona ENTER..."

ros2 bag record /odom /cmd_vel /tf -o bags/rc0_val_giro &
BAG_PID=$!

sleep 2

ros2 run capytown_esan calibrate_beff --ros-args \
-p b_eff:=$BEFF \
-p target_angle_deg:=360.0 \
-p angular_vel:=0.5

ros2 topic pub --once \
/cmd_vel geometry_msgs/msg/Twist "{}"

sleep 1

kill -INT $BAG_PID
wait $BAG_PID 2>/dev/null

echo ""
echo "VALIDACION DE GIRO TERMINADA."
echo "Bag: bags/rc0_val_giro"
