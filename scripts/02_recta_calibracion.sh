#!/bin/bash

source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=20
source /root/Grupo2-S004/install/setup.bash

cd /root/Grupo2-S004

RUN=${1:-1}

if [ "$RUN" = "final" ]; then
    BAG="bags/rc0_recta"
else
    BAG="bags/rc0_recta_prueba${RUN}"
fi

if [ -e "$BAG" ]; then
    echo "ERROR: ya existe $BAG"
    echo "Usa otro numero de corrida."
    exit 1
fi

echo "======================================"
echo " PARTE B - RECTA CALIBRACION A3"
echo " Corrida: $RUN"
echo "======================================"
echo ""
echo "Coloca el robot exactamente en el inicio."
read -p "Presiona ENTER cuando esté listo..."

ros2 bag record /odom /cmd_vel /tf -o "$BAG" &
BAG_PID=$!

sleep 2

echo "MOVIMIENTO: 0.10 m/s durante 10 s"

ros2 topic pub --rate 10 --times 100 \
/cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.10}}"

echo "FRENANDO..."

ros2 topic pub --once \
/cmd_vel geometry_msgs/msg/Twist "{}"

sleep 1

kill -INT $BAG_PID
wait $BAG_PID 2>/dev/null

echo ""
echo "RECTA TERMINADA."
echo "Bag guardado en: $BAG"
echo ""
echo "Ahora mide:"
echo "  d_real"
echo "  d_odom"
echo "  desvio_lateral"
