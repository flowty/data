import os
import tempfile

import flowty_data.rcmcf.fetch_repo as fetch_repo


def _download(dir):
    dirname = os.path.dirname(dir)
    dir = dirname if dirname else tempfile.gettempdir()
    fetch_repo.download(
        "flowty", "flow-first-route-next-heuristic-shipping-network-design", dir
    )


def _calculate_speed(distance, numVessels, numRotationEdges):
    availableTime = 168 * numVessels - 24 * numRotationEdges
    return distance / availableTime


def _read_networkCostName(dataDir, instancefile, rotations):
    speed = []
    capacities = []
    with open(os.path.join(dataDir, instancefile), "r") as f:
        line = f.readline()
        line = f.readline()
        while line:
            rotationId, capacity, distance, numVessels, _, _, _, _, _, _ = [
                int(x) for x in line.split(";")
            ]
            numRotationEdges = len(rotations[rotationId])
            speed.append(_calculate_speed(distance, numVessels, numRotationEdges))
            capacities.append(capacity)
            line = f.readline()
    return speed, capacities


def _read_networkRotationSol(dataDir, instancefile):
    rotations = {}
    with open(os.path.join(dataDir, instancefile), "r") as f:
        line = f.readline()
        line = f.readline()
        currentRotationId = -1
        rotation = []
        while line:
            rotationId, _, port, _, _, _, _ = line.split(";")
            if currentRotationId != int(rotationId):
                if currentRotationId != -1:
                    rotations[currentRotationId] = rotation
                rotation = []
            currentRotationId = int(rotationId)
            rotation.append(port)
            line = f.readline()
    rotations[currentRotationId] = rotation
    return rotations


def _read_rotations(instance: str, dir: str):
    instanceDir = instance.split("-")[0]
    dataDir = os.path.join(dir, "Speciale/BestSolutions", instanceDir)
    networkCostFilename = instance + "NetworkCost.csv"
    rotationsSolFilename = instance + "RotationSol.csv"
    name = instance
    speed = None
    capacities = None
    rotations = None
    rotations = _read_networkRotationSol(dataDir, rotationsSolFilename)
    speed, capacities = _read_networkCostName(dataDir, networkCostFilename, rotations)
    rotations = [r for id, r in rotations.items()]
    bunch = (name, rotations, speed, capacities)
    return bunch


def fetch_rotations(instance, dir):
    _download(dir)
    return _read_rotations(instance, dir)
