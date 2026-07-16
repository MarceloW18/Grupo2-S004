# RC-0 — Primer arranque y calibración del robot

## Grupo
Grupo 2

## Sección
S-004

## Variantes
- Calibración: A3 — Hombro
- Validación: A4 — Gancho

## Configuración ROS
- ROS 2: Humble
- ROS_DOMAIN_ID: 20
- Robot: MicroROS-Pi5

## Parámetros finales
- wheel_radius (r): 0.03679 m
- wheel_separation / b_eff: 0.2520 m

## Integrantes y roles
- Patrick — Integración
- Marcelo — Control
- Jeferson — Planificación
- Steven — Percepción

## Resultados

### Parte A — Arranque
Se verificó la comunicación placa → micro-ROS → ROS 2 y la disponibilidad de los tópicos principales.

### Parte B — Calibración lineal
Se calibró el radio de rueda mediante recorridos rectos de 1.0 m.

Valor final:
- r = 0.03679 m

### Parte C — Calibración de giro
Se calibró el ancho de vía efectivo mediante giros de 360°.

Valor final:
- b_eff = 0.2520 m

### Parte D — Validación
Se validó la calibración en la variante A4 sin recalibrar los parámetros obtenidos en A3.

### Parte E — Gráficas
El script `plot_odom.py` procesa los rosbag y genera:
- trayectoria x-y
- orientación theta(t)

Bags procesados:
- rc0_recta
- rc0_giro
- rc0_val_recta
- rc0_val_giro
