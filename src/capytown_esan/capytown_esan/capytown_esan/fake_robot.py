#!/usr/bin/env python3
"""
fake_robot.py - Simulador minimo del Yahboom para probar el paquete SIN hardware.

Permite correr TODO el pipeline (teleop, calibrate_beff, grabar bag, error_odom)
en un workspace completamente independiente, sin el robot real ni paquetes de
Yahboom. Habla por los MISMOS topicos estandar: suscribe /cmd_vel, publica /odom
y el tf odom->base_link.

POR QUE SIRVE PARA ENSENHAR LA CALIBRACION
------------------------------------------
Modela el desajuste real del skid-steer con dos parametros:
  - wheel_separation (b_eff_model): el b_eff que "cree" la odometria (= wheel_params.yaml)
  - b_eff_true: el track efectivo REAL (oculto, simula el slip)

La odometria (/odom) integra la velocidad angular COMANDADA (omega_cmd), mientras
que la rotacion FISICA real avanza a:

      omega_fisico = omega_cmd * (b_eff_model / b_eff_true)

Asi, si b_eff_model != b_eff_true, /odom y la realidad divergen, exactamente como
en el robot real. La pose fisica "verdadera" se publica en /odom_true para que el
alumno la lea (hace de "transportador") y la meta en calibrate_beff.

DEMO DE CALIBRACION (sin robot):
  1) ros2 run capytown_esan fake_robot --ros-args -p b_eff_true:=0.27
  2) ros2 run capytown_esan calibrate_beff --ros-args -p b_eff:=0.24   # gira hasta /odom=360
  3) lee el yaw fisico:  ros2 topic echo /odom_true   (o el log de fake_robot)
  4) mete ese angulo en calibrate_beff -> debe devolver b_eff ~= 0.27
"""
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64
from tf2_ros import TransformBroadcaster


def quat_from_yaw(yaw):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class FakeRobot(Node):
    def __init__(self):
        super().__init__('fake_robot')
        self.declare_parameter('wheel_separation', 0.24)   # b_eff_model (lo que cree la odom)
        self.declare_parameter('b_eff_true', 0.27)          # track efectivo REAL (oculto)
        self.declare_parameter('rate_hz', 50.0)

        self.b_model = float(self.get_parameter('wheel_separation').value)
        self.b_true = float(self.get_parameter('b_eff_true').value)
        self.rate = float(self.get_parameter('rate_hz').value)

        # Pose estimada por odometria (lo que reporta /odom)
        self.x_o = self.y_o = self.yaw_o = 0.0
        # Pose fisica real (verdad de campo)
        self.x_t = self.y_t = self.yaw_t = 0.0

        self.v = 0.0
        self.w_cmd = 0.0

        self.sub = self.create_subscription(Twist, '/cmd_vel', self._cmd_cb, 10)
        self.pub_odom = self.create_publisher(Odometry, '/odom', 20)
        self.pub_true = self.create_publisher(Odometry, '/odom_true', 20)
        # Yaw fisico acumulado (sin envolver) en grados -> hace de "transportador"
        self.pub_yaw = self.create_publisher(Float64, '/true_yaw_deg', 20)
        self.tf_bc = TransformBroadcaster(self)

        self.dt = 1.0 / self.rate
        self.timer = self.create_timer(self.dt, self._step)
        self.get_logger().info(
            f'fake_robot: b_eff_model={self.b_model:.4f}  b_eff_true={self.b_true:.4f}  '
            f'(ratio fisico/odom = {self.b_model / self.b_true:.4f})')

    def _cmd_cb(self, msg):
        self.v = msg.linear.x
        self.w_cmd = msg.angular.z

    def _step(self):
        dt = self.dt
        # Odometria: integra la omega COMANDADA (lo que cree el modelo)
        self.yaw_o += self.w_cmd * dt
        self.x_o += self.v * math.cos(self.yaw_o) * dt
        self.y_o += self.v * math.sin(self.yaw_o) * dt
        # Fisica real: gira segun el desajuste de track efectivo
        w_phys = self.w_cmd * (self.b_model / self.b_true)
        self.yaw_t += w_phys * dt
        self.x_t += self.v * math.cos(self.yaw_t) * dt
        self.y_t += self.v * math.sin(self.yaw_t) * dt

        now = self.get_clock().now().to_msg()
        self._publish(self.pub_odom, now, self.x_o, self.y_o, self.yaw_o)
        self._publish(self.pub_true, now, self.x_t, self.y_t, self.yaw_t)
        self.pub_yaw.publish(Float64(data=math.degrees(self.yaw_t)))

        # tf odom -> base_link (de la pose estimada)
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x_o
        t.transform.translation.y = self.y_o
        qx, qy, qz, qw = quat_from_yaw(self.yaw_o)
        t.transform.rotation.x, t.transform.rotation.y = qx, qy
        t.transform.rotation.z, t.transform.rotation.w = qz, qw
        self.tf_bc.sendTransform(t)

    @staticmethod
    def _publish(pub, stamp, x, y, yaw):
        o = Odometry()
        o.header.stamp = stamp
        o.header.frame_id = 'odom'
        o.child_frame_id = 'base_link'
        o.pose.pose.position.x = x
        o.pose.pose.position.y = y
        qx, qy, qz, qw = quat_from_yaw(yaw)
        o.pose.pose.orientation.x = qx
        o.pose.pose.orientation.y = qy
        o.pose.pose.orientation.z = qz
        o.pose.pose.orientation.w = qw
        pub.publish(o)


def main():
    rclpy.init()
    node = FakeRobot()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
