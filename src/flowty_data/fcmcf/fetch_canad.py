import os
import tempfile
import flowty_data.fetch


# From version 1
def _getInstancename(instance, name):
    end = ".dow"
    if instance.endswith("N"):
        end = ".dat"
    return name + end


def _download(instance, dir):
    instance_lookup = {
        "Canad-C": "C.tgz",
        "Canad-C+": "CPlus.tgz",
        "Canad-R": "R.tgz",
        # "Canad-N": "CanadN.tgz",
    }
    filename = instance_lookup[instance]
    url = f"http://groups.di.unipi.it/optimize/Data/MMCF/{instance_lookup[instance]}"
    flowty_data.fetch.fetch_tgz(filename, url, dir)


# From version 1
def _readDow(instance, name, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    instanceName = _getInstancename(instance, name)
    filename = os.path.join(downloadDir, instanceName)
    numN = 0
    numE = 0
    numK = 0
    E = []
    C = []
    U = []
    F = []
    O = []
    D = []
    B = []
    with open(filename, "r") as f:
        f.readline()
        numN, numE, numK = [int(w) for w in f.readline().split(" ") if w.strip()]
        for _ in range(numE):
            source, target, cost, capacity, fixed, any1, any2 = [
                int(w) for w in f.readline().split(" ") if w.strip()
            ]
            E.append((source - 1, target - 1))
            C.append(cost)
            U.append(capacity)
            F.append(fixed)
        for _ in range(numK):
            origin, dest, demand = [
                int(w) for w in f.readline().split(" ") if w.strip()
            ]
            O.append(origin - 1)
            D.append(dest - 1)
            B.append(demand)
    return name, numN, numE, numK, E, C, U, F, O, D, B


def _readAll(instance, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    data = []
    for filename in os.listdir(downloadDir):
        if filename.endswith(".dow"):
            name = filename.rstrip(".dow")
            data.append(_readDow(instance, name, dir))
            os.remove(os.path.join(downloadDir, filename))
    return data


def fetch(instance, dir=None):
    if dir and not os.path.exists(dir):
        raise FileExistsError(f"No such dir {dir}")
    _download(instance, dir)
    return _readAll(instance, dir)
