import sys
import argparse
import os

from flowty_data.vrptw.fetch_solomonhg import fetch


def _convert(instance, dataSet, out, numCustomers=None):
    for data in dataSet:
        name, n, m, E, C, D, q, T, A, B, X, Y = data
        if numCustomers:
            name = f"{name}_{numCustomers}"
        lines = [
            "c vehicle routing problem with time windows\n",
            f"c {instance} {name}\n",
            "c\n",
            "c problem vertices edges capacity\n",
            f"p vrptw {n} {m} {q}\n",
            "c\n",
            "c vertex a b demand x y\n",
        ]
        for i, a, b, d, x, y in zip(range(n), A, B, D, X, Y):
            lines += [f"v {i} {a} {b} {d} {x} {y}\n"]
        lines += ["c\n", "c source target cost time\n"]
        for (s, t), c, time in zip(E, C, T):
            lines += [f"a {s} {t} {c} {time}\n"]

        filename = os.path.join(out, f"{name}.txt")
        with open(filename, "w") as f:
            f.writelines(lines)


def convert():
    argv = sys.argv[1:]
    argv.append("--instance")
    argv.append("solomon")
    argv.append("--out")
    argv.append("data/vrptw")
    # argv.append("--all")

    parser = argparse.ArgumentParser(description="Converts vrptw data to other format")
    parser.add_argument(
        "--type", help="Converts vrptw data to Flowty format", default="mcf"
    )
    parser.add_argument("--instance", help="instance name")
    parser.add_argument("--out", help="place to write files", default=".")
    parser.add_argument(
        "--all",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="convert all",
    )
    args = parser.parse_args(argv)

    instances = ["solomon", "homberger"]
    downloadDir = "data/vrptw/pucrio"
    numCustomers = None  # 50
    os.makedirs(downloadDir, exist_ok=True)
    if args.all:
        for instance in instances:
            dataSet = fetch(instance, dir=downloadDir, numCustomers=numCustomers)
            _convert(instance, dataSet, args.out, numCustomers=numCustomers)
    else:
        dataSet = fetch(args.instance, dir=downloadDir, numCustomers=numCustomers)
        _convert(args.instance, dataSet, args.out, numCustomers=numCustomers)
