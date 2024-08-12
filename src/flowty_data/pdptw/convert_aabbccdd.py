import sys
import argparse
import gzip
import io
import os

from flowty_data.pdptw.fetch_aabbccdd import fetch

def _convert(dataSet, out):
    for data in dataSet:
        name, n, m, E, C, D, q, T, A, B, X, Y = data
        lines = [
            "c pickup and develivery with time windows\n",
            f"c {name}\n",
            "c\n",
            "c problem requests edges capacity\n",
            f"p pdptw {n} {m} {q}\n",
            "c\n",
            "c vertex a b demand x y\n",
        ]
        for i, a, b, d, x, y in zip(range(2*n+2), A, B, D, X, Y):
            lines += [f"v {i} {a} {b} {d} {x} {y}\n"]
        lines += ["c\n", "c source target cost time\n"]
        for (s, t), c, time in zip(E, C, T):
            lines += [f"a {s} {t} {c} {time}\n"]

        filename = os.path.join(out, f"{name}.txt.gz")
        with gzip.open(filename, 'wb') as output:
            with io.TextIOWrapper(output, encoding='utf-8') as encode:
                encode.writelines(lines)


def convert():
    argv = sys.argv[1:]
    argv.append("--infile")
    argv.append("data/pdptw/temp/AABBCCDD.zip")
    argv.append("--out")
    argv.append("data/pdptw")

    parser = argparse.ArgumentParser(description="Converts pdptw (aabbccdd) data to Flowty format")
    parser.add_argument("--infile", help="path to zip-file")
    parser.add_argument("--out", help="place to write files", default=".")
    args = parser.parse_args(argv)

    dataSet = fetch(args.infile)
    _convert(dataSet, args.out)
