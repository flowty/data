import os
import tempfile
import flowty_data.fetch


def _download(instance, dir):
    instance_lookup = {
        "planar": "planar.tgz",
        "grid": "grid.tgz",
    }
    filename = instance_lookup[instance]
    url = f"http://groups.di.unipi.it/optimize/Data/MMCF/{instance_lookup[instance]}"
    flowty_data.fetch.fetch_tgz(filename, url, dir)


def _read(instance, num, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    instanceName = instance + str(num)
    filename = os.path.join(downloadDir, instanceName)
    n = 0
    m = 0
    k = 0
    E = []
    C = []
    U = []
    O = []
    D = []
    B = []
    with open(filename, "r") as f:
        n = int(f.readline())
        m = int(f.readline())
        k = int(f.readline())
        for _ in range(m):
            source, target, cost, capacity = [
                int(w) for w in f.readline().split(" ") if w.strip()
            ]
            E.append((source - 1, target - 1))
            C.append(cost)
            U.append(capacity)
        for _ in range(k):
            origin, dest, demand = [
                int(w) for w in f.readline().split(" ") if w.strip()
            ]
            O.append(origin - 1)
            D.append(dest - 1)
            B.append(demand)
    return instanceName, n, m, k, E, C, U, O, D, B


def _readAll(instance, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    data = []
    for filename in os.listdir(downloadDir):
        if filename.startswith(instance) and not filename.endswith(".tgz"):
            num = int(filename.lstrip(instance))
            data.append(_read(instance, num, dir))
    return data


def fetch(instance, dir=None):
    if dir and not os.path.exists(dir):
        raise FileExistsError(f"No such dir {dir}")
    _download(instance, dir)
    return _readAll(instance, dir)
