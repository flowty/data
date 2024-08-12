import os
import tempfile
import math
import zipfile

def _unzip(filename, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    with zipfile.ZipFile(filename, "r") as file:
       file.extractall(downloadDir)


def _readNodeLine(file):
    id, x, y, s, d, a, b = file.readline().split()
    return int(id), float(x), float(y), int(s), int(d), int(a), int(b)


def _read(filename, dir):
    filepath = os.path.join(dir, filename)
    scale = 10
    with open(filepath, "r") as f:
        _, n, _, q, _ = (int(val) for val in f.readline().split())
        X = []
        Y = []
        D = []
        A = []
        B = []
        S = []
        for i in range(2*n+2):
            id, x, y, s, d, a, b = _readNodeLine(f)
            X.append(x)
            Y.append(y)
            D.append(d)
            A.append(a * scale)
            B.append(b * scale)
            S.append(s * scale)
        E = []
        C = []
        T = []
        for i in range(2*n+1):
            for j in range(1, 2*n+2):
                if (i == 0 and j == 2*n+1) or i == j or i == j + n:
                    continue
                value = int(
                    math.sqrt(math.pow(X[i] - X[j], 2) + math.pow(Y[i] - Y[j], 2))
                    * scale
                )
                E.append((i, j))
                C.append(value)
                T.append(value + S[i])
        name = filename
        m = len(E)
    return name, n, m, E, C, D, q, T, A, B, X, Y


def _readAll(dir):
    data = []
    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            continue
        data.append(_read(filename, dir))
    return data


def fetch(inpath, dir=None):
    if dir and not os.path.exists(dir):
        raise FileExistsError(f"No such dir {dir}")
    dir = dir if dir else tempfile.gettempdir()
    unpackDir = os.path.join(dir, "AABBCCDD")
    _unzip(inpath, unpackDir)
    return _readAll(unpackDir)
