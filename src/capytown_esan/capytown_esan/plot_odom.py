#!/usr/bin/env python3

import os
import sys
import math
import yaml

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry


def storage_id(bag):
    """Lee metadata.yaml y devuelve sqlite3, mcap, etc."""
    metadata_path = os.path.join(bag, "metadata.yaml")

    if not os.path.isfile(metadata_path):
        raise FileNotFoundError(
            f"No existe metadata.yaml en: {bag}"
        )

    with open(metadata_path, "r") as f:
        metadata = yaml.safe_load(f)

    return metadata["rosbag2_bagfile_information"]["storage_identifier"]


def read_pose(bag, topic="/odom"):
    """Lee t, x, y y theta desde /odom."""
    reader = SequentialReader()

    sid = storage_id(bag)

    print(f"Bag: {bag}")
    print(f"Storage detectado: {sid}")

    reader.open(
        StorageOptions(
            uri=bag,
            storage_id=sid
        ),
        ConverterOptions(
            input_serialization_format="cdr",
            output_serialization_format="cdr"
        )
    )

    t = []
    x = []
    y = []
    th = []

    t0 = None

    while reader.has_next():
        tp, data, stamp = reader.read_next()

        if tp != topic:
            continue

        m = deserialize_message(data, Odometry)

        if t0 is None:
            t0 = stamp

        # Tiempo relativo desde el primer mensaje /odom
        t.append((stamp - t0) * 1e-9)

        x.append(m.pose.pose.position.x)
        y.append(m.pose.pose.position.y)

        q = m.pose.pose.orientation

        theta = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        th.append(math.degrees(theta))

    if not t:
        raise RuntimeError(
            f"No se encontraron mensajes {topic} en {bag}"
        )

    return t, x, y, th


def make_plots(bag):
    t, x, y, th = read_pose(bag)

    bag_name = os.path.basename(os.path.normpath(bag))

    os.makedirs("plots", exist_ok=True)

    # --------------------------
    # Trayectoria X-Y
    # --------------------------
    plt.figure(figsize=(7, 6))
    plt.plot(x, y, linewidth=1.5)
    plt.scatter(x[0], y[0], label="Inicio")
    plt.scatter(x[-1], y[-1], label="Fin")

    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title(f"Trayectoria x-y — {bag_name}")

    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    xy_file = os.path.join(
        "plots",
        f"{bag_name}_xy.png"
    )

    plt.savefig(xy_file, dpi=150)
    plt.close()

    # --------------------------
    # Orientación theta(t)
    # --------------------------
    plt.figure(figsize=(8, 5))
    plt.plot(t, th, linewidth=1.5)

    plt.xlabel("Tiempo [s]")
    plt.ylabel("θ [grados]")
    plt.title(f"Orientación θ(t) — {bag_name}")

    plt.grid(True)
    plt.tight_layout()

    theta_file = os.path.join(
        "plots",
        f"{bag_name}_theta.png"
    )

    plt.savefig(theta_file, dpi=150)
    plt.close()

    print("")
    print("OK - Graficas generadas:")
    print(f"  {xy_file}")
    print(f"  {theta_file}")
    print(f"  Mensajes /odom: {len(t)}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso:")
        print(
            "python3 plot_odom.py "
            "bags/<nombre_del_bag>"
        )
        sys.exit(1)

    bag = sys.argv[1]

    if not os.path.isdir(bag):
        print(f"ERROR: no existe: {bag}")
        sys.exit(1)

    make_plots(bag)
