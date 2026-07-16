#!/usr/bin/env bash

source /opt/ros/humble/setup.bash
source /root/Grupo2-S004/install/setup.bash 2>/dev/null || true

export ROS_DOMAIN_ID=20
export ROS_LOCALHOST_ONLY=0

cd /root/Grupo2-S004

BAG="bags/rc0_val_recta"
BAG_PID=""
MOVE_PID=""

ZERO="{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
RECTA="{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

stop_robot() {
    echo ""
    echo ">>> DETENIENDO ROBOT..."

    ros2 topic pub \
        --rate 20 \
        --times 40 \
        /cmd_vel \
        geometry_msgs/msg/Twist \
        "$ZERO" >/dev/null 2>&1 || true

    echo ">>> Velocidad = 0"
}

cleanup() {
    trap - INT TERM EXIT

    if [ -n "${MOVE_PID:-}" ] && kill -0 "$MOVE_PID" 2>/dev/null; then
        kill -INT "$MOVE_PID" 2>/dev/null || true
        wait "$MOVE_PID" 2>/dev/null || true
    fi

    stop_robot

    if [ -n "${BAG_PID:-}" ] && kill -0 "$BAG_PID" 2>/dev/null; then
        echo ">>> Cerrando rosbag..."
        kill -INT "$BAG_PID" 2>/dev/null || true
        wait "$BAG_PID" 2>/dev/null || true
    fi
}

interrumpido() {
    echo ""
    echo "======================================"
    echo " INTERRUPCION DETECTADA - Ctrl+C"
    echo "======================================"
    cleanup
    exit 130
}

trap interrumpido INT TERM
trap cleanup EXIT

echo "======================================"
echo " PARTE D - VALIDACION A4 - RECTAS"
echo "======================================"
echo "Velocidad: 0.10 m/s"
echo "Duracion por recta: 10 s"
echo "Direccion: ESTE -> OESTE"
echo "======================================"

# Guardar cualquier bag anterior
if [ -d "$BAG" ]; then
    OLD="${BAG}_viejo_$(date +%H%M%S)"
    echo "Bag anterior encontrado."
    echo "Moviendo a: $OLD"
    mv "$BAG" "$OLD"
fi

echo ""
echo "Iniciando rosbag..."

ros2 bag record \
    -o "$BAG" \
    /odom \
    /tf \
    /cmd_vel &

BAG_PID=$!

sleep 2

# -------------------------------
# RECTA 1
# -------------------------------

echo ""
echo "======================================"
echo " RECTA 1"
echo "======================================"
echo "Coloca el robot en la marca inicial."
read -r -p "Presiona ENTER para iniciar RECTA 1..."

echo ">>> RECTA 1 iniciada"

ros2 topic pub \
    --rate 10 \
    --times 100 \
    /cmd_vel \
    geometry_msgs/msg/Twist \
    "$RECTA" &

MOVE_PID=$!
wait "$MOVE_PID" || true
MOVE_PID=""

stop_robot

echo ">>> RECTA 1 TERMINADA."
echo ">>> Mide inicio y final antes de continuar."

# -------------------------------
# RECTA 2
# -------------------------------

echo ""
echo "======================================"
echo " RECTA 2"
echo "======================================"
echo "Vuelve a colocar el robot en la marca inicial."
read -r -p "Presiona ENTER para iniciar RECTA 2..."

echo ">>> RECTA 2 iniciada"

ros2 topic pub \
    --rate 10 \
    --times 100 \
    /cmd_vel \
    geometry_msgs/msg/Twist \
    "$RECTA" &

MOVE_PID=$!
wait "$MOVE_PID" || true
MOVE_PID=""

stop_robot

echo ">>> RECTA 2 TERMINADA."

# Parada extra de seguridad
stop_robot

# Cerramos manualmente antes de salir
trap - EXIT
cleanup

echo ""
echo "======================================"
echo " VALIDACION DE RECTAS TERMINADA"
echo "======================================"
echo "Bag: $BAG"
echo "Robot detenido."
