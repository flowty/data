import os
import tempfile
import math
from itertools import islice
import flowty_data.fetch


def _download(instance, dir):
    instance_lookup = {
        "solomon": "Vrp-Set-Solomon.tgz",
        "homberger": "Vrp-Set-HG.tgz",
    }
    filename = instance_lookup[instance]
    url = f"http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/{filename}"
    flowty_data.fetch.fetch_tgz(filename, url, dir)


def _skipLines(file, num):
    for _ in range(num):
        file.readline()


def _read(instance, dir, numCustomers=None):
    downloadDir = dir if dir else tempfile.gettempdir()
    filename = os.path.join(downloadDir, instance)
    scale = 10
    with open(filename, "r") as f:
        name = f.readline().strip("\n").strip()
        _skipLines(f, 3)
        line = f.readline()
        _, q = (int(val) for val in line.split())
        _skipLines(f, 4)
        line = f.readline()
        X = []
        Y = []
        D = []
        A = []
        B = []
        S = []
        while line:
            _, x, y, d, a, b, s = (int(val) for val in line.split())
            X.append(x)
            Y.append(y)
            D.append(d)
            A.append(a * scale)
            B.append(b * scale)
            S.append(s * scale)
            line = f.readline()
        if numCustomers:
            X = X[: numCustomers + 1]
            Y = Y[: numCustomers + 1]
            D = D[: numCustomers + 1]
            A = A[: numCustomers + 1]
            B = B[: numCustomers + 1]
            S = S[: numCustomers + 1]
        # Clone depot
        X.append(X[0])
        Y.append(Y[0])
        D.append(D[0])
        A.append(A[0])
        B.append(B[0])
        S.append(S[0])
        E = []
        C = []
        T = []
        n = len(X)
        for i in range(n - 1):
            for j in range(1, n):
                if (i == 0 and j == n - 1) or i == j:
                    continue
                value = int(
                    math.sqrt(math.pow(X[i] - X[j], 2) + math.pow(Y[i] - Y[j], 2))
                    * scale
                )
                C.append(value)
                T.append(value + S[i])
                E.append((i, j))
        m = len(E)
    return name, n, m, E, C, D, q, T, A, B, X, Y


def _readAll(instance, dir, numCustomers=None):
    instance_lookup = {
        "solomon": "Vrp-Set-Solomon",
        "homberger": "Vrp-Set-HG/Vrp-Set-HG",
    }
    downloadDir = dir if dir else tempfile.gettempdir()
    downloadDir = os.path.join(downloadDir, instance_lookup[instance])
    data = []
    for filename in os.listdir(downloadDir):
        if filename.endswith(".sol") or filename == "results.txt":
            continue
        data.append(_read(filename, downloadDir, numCustomers))
    return data


def fetch(instance, dir=None, numCustomers=None):
    if dir and not os.path.exists(dir):
        raise FileExistsError(f"No such dir {dir}")
    _download(instance, dir)
    return _readAll(instance, dir, numCustomers)
