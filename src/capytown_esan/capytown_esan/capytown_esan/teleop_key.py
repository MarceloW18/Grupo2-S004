#!/usr/bin/env python3
"""
teleop_key.py - Teleoperacion por teclado (WASD) para el Yahboom MicroROS-Pi5.

Publica geometry_msgs/Twist en /cmd_vel. Sirve para mover el robot a mano y
verificar que el bringup y la conexion con el ESP32 funcionan ANTES de calibrar.

Teclas:
    w / s : adelante / atras
    a / d : girar izquierda / derecha (sobre el sitio)
    espacio o k : frenar (Twist cero)
    + / - : subir / bajar la velocidad
    q : salir

USO:
    ros2 run capytown_esan teleop_key
"""
import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

HELP = """
-------------------------------------------------
 Teleop CapyTown  (publica en /cmd_vel)
   w/s : adelante/atras    a/d : girar izq/der
   espacio o k : frenar
   + / - : velocidad       q : salir
-------------------------------------------------
"""


def get_key(settings, timeout=0.1):
    tty.setraw(sys.stdin.fileno())
    r, _, _ = select.select([sys.stdin], [], [], timeout)
    key = sys.stdin.read(1) if r else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class TeleopKey(Node):
    def __init__(self):
        super().__init__('teleop_key')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lin = 0.10   # m/s recomendado por el reto
        self.ang = 0.50   # rad/s recomendado por el reto


def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = TeleopKey()
    print(HELP)
    print(f' v_lineal = {node.lin:.2f} m/s   v_angular = {node.ang:.2f} rad/s')
    twist = Twist()
    try:
        while rclpy.ok():
            key = get_key(settings)
            twist = Twist()
            if key == 'w':
                twist.linear.x = node.lin
            elif key == 's':
                twist.linear.x = -node.lin
            elif key == 'a':
                twist.angular.z = node.ang
            elif key == 'd':
                twist.angular.z = -node.ang
            elif key in (' ', 'k'):
                twist = Twist()
            elif key == '+':
                node.lin *= 1.1
                node.ang *= 1.1
                print(f' v_lineal = {node.lin:.2f}  v_angular = {node.ang:.2f}')
            elif key == '-':
                node.lin *= 0.9
                node.ang *= 0.9
                print(f' v_lineal = {node.lin:.2f}  v_angular = {node.ang:.2f}')
            elif key == 'q':
                break
            node.pub.publish(twist)
    except Exception as e:
        print(e)
    finally:
        node.pub.publish(Twist())  # frenar al salir
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
