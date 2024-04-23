import os
import tempfile
import flowty_data.fetch


# From version 1
# _instance_lookup = {
#     "Canad-C": "C.tgz",
#     "Canad-C+": "CPlus.tgz",
#     "Canad-R": "R.tgz",
#     "Canad-N": "CanadN.tgz",
# }

# From version 1
def _getInstancename(instance, name):
    end = ".dow"
    if instance.endswith("N"):
        end = ".dat"
    return name + end


# def _download(instance, name):
#     tmpdir = tempfile.gettempdir()
#     filename = os.path.join(tmpdir, _instance_lookup[instance])
#     if not os.path.exists(filename):
#         url = (
#             f"http://groups.di.unipi.it/optimize/Data/MMCF/{_instance_lookup[instance]}"
#         )
#         headers = {"Accept": "application/zip"}
#         req = urllib.request.Request(url, headers=headers)
#         with urllib.request.urlopen(req) as response:
#             with open(filename, "wb") as out_file:
#                 shutil.copyfileobj(response, out_file)
#     instanceName = _getInstancename(instance, name) if name else None
#     instanceNames = []
#     with tarfile.open(filename, "r") as tf:
#         for member in tf.getmembers():
#             if not instanceName or member.name == instanceName:
#                 instanceNames.append(member.name)
#                 if not os.path.exists(os.path.join(tmpdir, member.name)):
#                     tf.extract(member, tmpdir)
#                 if instanceName:
#                     return
#         if instanceName:
#             raise TypeError(f"{name} not in {instance} data set")
#     return instanceNames




# def _readAllDow(instance, instanceNames):
#     tmpdir = tempfile.gettempdir()
#     data = []
#     for filename in os.listdir(tmpdir):
#         if filename.endswith(".dow") and filename in instanceNames:
#             name = filename.rstrip(".dow")
#             data.append(_readDow(instance, name))
#     return data


# def fetch(instance, name):
#     instanceNames = _download(instance, name)
#     if name:
#         instancename = _getInstancename(instance, name)
#         if instancename.endswith(".dow"):
#             return _readDow(instance, name)
#     return _readAllDow(instance, instanceNames)


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

# def _read(instance, num, dir):
#     downloadDir = dir if dir else tempfile.gettempdir()
#     instanceName = instance + str(num)
#     filename = os.path.join(downloadDir, instanceName)
#     n = 0
#     m = 0
#     k = 0
#     E = []
#     C = []
#     U = []
#     O = []
#     D = []
#     B = []
#     with open(filename, "r") as f:
#         n = int(f.readline())
#         m = int(f.readline())
#         k = int(f.readline())
#         for _ in range(m):
#             source, target, cost, capacity = [
#                 int(w) for w in f.readline().split(" ") if w.strip()
#             ]
#             E.append((source - 1, target - 1))
#             C.append(cost)
#             U.append(capacity)
#         for _ in range(k):
#             origin, dest, demand = [
#                 int(w) for w in f.readline().split(" ") if w.strip()
#             ]
#             O.append(origin - 1)
#             D.append(dest - 1)
#             B.append(demand)
#     return instanceName, n, m, k, E, C, U, O, D, B

# From version 1
# def _readAllDow(instance, instanceNames):
#     tmpdir = tempfile.gettempdir()
#     data = []
#     for filename in os.listdir(tmpdir):
#         if filename.endswith(".dow") and filename in instanceNames:
#             name = filename.rstrip(".dow")
#             data.append(_readDow(instance, name))
#     return data

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
