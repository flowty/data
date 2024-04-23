import sys
import argparse
import os

from flowty_data.fcmcf.fetch_canad import fetch

def _convert(dataSet, out):
    for data in dataSet:
        name, n, m, k, E, C, U, F, O, D, B = data
        lines = [
            "c fixed charge multi commodity flow\n",
            "c\n",
            "c problem vertices edges commodities\n",
            f"p fcmcf {n} {m} {k}\n",
            "c\n",
            "c origin destination demand\n",
        ]
        for o, d, b in zip(O, D, B):
            lines += [f"k {o} {d} {b}\n"]
        lines += ["c\n", "c source target cost capacity fixed\n"]
        for (s, t), c, u, f in zip(E, C, U, F):
            line = f"a {s} {t}"
            line += f" {c}"
            line += f" {u}"
            line += f" {f}"
            lines += [line + "\n"]

        filename = os.path.join(out, f"{name}.txt")
        with open(filename, "w") as f:
            f.writelines(lines)

def convert():
    argv = sys.argv[1:]
    # argv.append("--instance")
    # argv.append("Canad-C")
    argv.append("--out")
    argv.append("data/fcmcf")
    argv.append("--all")

    parser = argparse.ArgumentParser(description="Converts fcmcf data to other format")
    parser.add_argument(
        "--type", help="Converts fcmcf data to Flowty format", default="fcmcf"
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

    instances = ["Canad-C",
                "Canad-C+",
                "Canad-R",
                # "Canad-N"
                ]
    downloadDir = "data/fcmcf/unipi"
    os.makedirs(downloadDir, exist_ok=True)
    if args.all:
        for instance in instances:
            dataSet = fetch(instance, dir=downloadDir)
            _convert(dataSet, args.out)
    else:
        dataSet = fetch(args.instance, dir=downloadDir)
        _convert(dataSet, args.out)
