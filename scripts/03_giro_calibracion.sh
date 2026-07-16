#!/bin/bash

source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=20
source /root/Grupo2-S004/install/setup.bash

cd /root/Grupo2-S004

BEFF=$1
TIPO=${2:-prueba}

if [ -z "$BEFF" ]; then
    echo "Uso:"
    echo "./scripts/03_giro_calibracion.sh <b_eff>"
    echo ""
    echo "Ejemplo:"
    echo "./scripts/03_giro_calibracion.sh 0.205"
    exit 1
fi

echo "======================================"
echo " PARTE C - GIRO CALIBRACION A3"
echo " b_eff = $BEFF m"
echo "======================================"

if [ "$TIPO" = "final" ]; then

    if [ -e "bags/rc0_giro" ]; then
        echo "ERROR: bags/rc0_giro ya existe."
        exit 1
    fi

    ros2 bag record /odom /cmd_vel /tf -o bags/rc0_giro &
    BAG_PID=$!

    sleep 2
fi

read -p "Coloca el robot en G y presiona ENTER..."

ros2 run capytown_esan calibrate_beff --ros-args \
-p b_eff:=$BEFF \
-p target_angle_deg:=360.0 \
-p angular_vel:=-0.5

ros2 topic pub --once \
/cmd_vel geometry_msgs/msg/Twist "{}"

if [ "$TIPO" = "final" ]; then
    sleep 1
    kill -INT $BAG_PID
    wait $BAG_PID 2>/dev/null
    echo "Bag final guardado: bags/rc0_giro"
fi

echo ""
echo "GIRO TERMINADO."
echo "Mide el angulo real."
