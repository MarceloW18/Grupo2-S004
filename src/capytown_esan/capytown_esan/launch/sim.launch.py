#!/usr/bin/env python3
"""
sim.launch.py - Modo SIMULACION, 100% independiente (sin robot ni Yahboom).

Lanza solo el simulador fake_robot, que publica /odom y acepta /cmd_vel. Con esto
puedes probar teleop_key, calibrate_beff y error_odom en un workspace limpio.

    ros2 launch capytown_esan sim.launch.py
    # opcional: simular un desajuste de track efectivo
    ros2 launch capytown_esan sim.launch.py b_eff_true:=0.27
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    b_eff_true = LaunchConfiguration('b_eff_true', default='0.27')
    wheel_sep = LaunchConfiguration('wheel_separation', default='0.24')
    return LaunchDescription([
        DeclareLaunchArgument('b_eff_true', default_value='0.27',
                              description='Track efectivo REAL simulado (oculto a la odom)'),
        DeclareLaunchArgument('wheel_separation', default_value='0.24',
                              description='b_eff que cree la odometria (= wheel_params.yaml)'),
        Node(
            package='capytown_esan',
            executable='fake_robot',
            name='fake_robot',
            output='screen',
            parameters=[{'b_eff_true': b_eff_true, 'wheel_separation': wheel_sep}],
        ),
    ])
