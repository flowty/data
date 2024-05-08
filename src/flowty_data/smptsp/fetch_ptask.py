import os
import tempfile
import flowty_data.fetch


def _download(dir):
    filename = "ptask.zip"
    url = f"http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/{filename}"
    flowty_data.fetch.fetch_zip(filename, url, dir)


def _read(name, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    instanceName = name.rstrip(".dat")
    filename = os.path.join(downloadDir, name)
    n = 0
    S = []
    F = []
    B = []
    P = []
    T = []
    cost = 1
    with open(filename, "r") as f:
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        n = int(f.readline().split("=")[-1].strip())
        for _ in range(n):
            start, finish = [int(w) for w in f.readline().split(" ") if w.strip()]
            S.append(start)
            F.append(finish)
        m = int(f.readline().split("=")[-1].strip())
        P = [[] for _ in range(n)]
        T = [[] for _ in range(m)]
        for i in range(m):
            data = [w for w in f.readline().split(" ") if w.strip()][1:]
            T[i] = [int(w) for w in data]
            for j in T[i]:
                P[j].append(i)
            B.append(cost)
    return instanceName, n, m, S, F, B, P, T


def _readAll(dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    data = []
    for filename in os.listdir(downloadDir):
        if filename.endswith(".zip"):
            continue
        data.append(_read(filename, dir))
    return data


def fetch(dir=None):
    if dir and not os.path.exists(dir):
        raise FileExistsError(f"No such dir {dir}")
    _download(dir)
    return _readAll(dir)
