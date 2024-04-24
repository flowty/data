import sys
import argparse
import os

from flowty_data.smptsp.fetch_ptask import fetch


def _convert(dataSet, out):
    for data in dataSet:
        name, n, m, S, F, B, P, T = data
        lines = [
            "c Shift Minimisation Personnel Task Scheduling Problem (SMPTSP)\n",
            f"c {name}\n" "c\n",
            "c problem jobs shifts\n",
            f"p smptsp {n} {m}\n",
            "c\n",
            "c job start finish \n",
        ]
        for j, (s, f) in enumerate(zip(S, F)):
            lines += [f"c {j} {s} {f}\n"]
        lines += [
            "c\n",
            "c shift cost source target num_qualifications qualifications\n",
        ]
        for i, (t, b) in enumerate(zip(T, B)):
            line = f"k {i} {b} {n*2} {n*2+1} {len(t)}"
            for q in t:
                line += f" {q}"
            lines += [line + "\n"]
        lines += ["c\n", "c graph source target\n"]
        for i in range(m):
            source = n * 2
            target = n * 2 + 1
            prev = source
            start = [(j, S[j], True) for j in T[i]]
            finish = [(j, F[j], False) for j in T[i]]
            vertices = sorted(start + finish, key=lambda x: x[1])
            for j, t, isStart in vertices:
                vid = j if isStart else j + n
                lines += [f"a {i} {prev} {vid}\n"]
                if not isStart:
                    lines += [f"a {i} {j} {vid}\n"]
                prev = vid
            lines += [f"a {i} {prev} {target}\n"]
        filename = os.path.join(out, f"{name}.txt")
        with open(filename, "w") as f:
            f.writelines(lines)


def convert():
    argv = sys.argv[1:]
    argv.append("--out")
    argv.append("data/smptsp")

    parser = argparse.ArgumentParser(description="Converts smptsp data to other format")
    parser.add_argument(
        "--type", help="Converts smptsp data to Flowty format", default="smptsp"
    )
    parser.add_argument("--out", help="place to write files", default=".")
    args = parser.parse_args(argv)

    downloadDir = "data/smptsp/orlib"
    os.makedirs(downloadDir, exist_ok=True)
    dataSet = fetch(dir=downloadDir)
    _convert(dataSet, args.out)
