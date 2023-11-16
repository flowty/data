import sys
import argparse
import os

from flowty_data.mcf.fetch_planargrid import fetch


def _convert(dataSet, out):
    for data in dataSet:
        name, n, m, k, E, C, U, O, D, B = data
        lines = [
            "c multi commodity flow\n",
            f"c {name}\n" "c\n",
            "c problem vertices edges commodities\n",
            f"p mcf {n} {m} {k}\n",
            "c\n",
            "c origin destination demand\n",
        ]
        for o, d, b in zip(O, D, B):
            lines += [f"k {o} {d} {b}\n"]
        lines += ["c\n", "c source target cost capacity\n"]
        for (s, t), c, u in zip(E, C, U):
            lines += [f"a {s} {t} {c} {u}\n"]

        filename = os.path.join(out, f"{name}.txt")
        with open(filename, "w") as f:
            f.writelines(lines)


def convert():
    argv = sys.argv[1:]
    # argv.append("--instance")
    # argv.append("grid")
    argv.append("--out")
    argv.append("data/mcf")
    argv.append("--all")

    parser = argparse.ArgumentParser(description="Converts mcf data to other format")
    parser.add_argument(
        "--type", help="Converts mcf data to Flowty format", default="mcf"
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

    instances = ["grid", "planar"]
    downloadDir = "data/mcf/unipi"
    os.makedirs(downloadDir, exist_ok=True)
    if args.all:
        for instance in instances:
            dataSet = fetch(instance, dir=downloadDir)
            _convert(dataSet, args.out)
    else:
        dataSet = fetch(args.instance, dir=downloadDir)
        _convert(dataSet, args.out)
