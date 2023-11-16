import os
import tempfile
import math
import csv
import io
from typing import Dict, Any, Tuple, List

import flowty_data.linerlib.fetch_repo as fetch_repo


def _download(dir):
    dirname = os.path.dirname(dir)
    dir = dirname if dirname else tempfile.gettempdir()
    branch = "worldsmall_demand_fix"
    fetch_repo.download("flowty", "LINERLIB", dir, branch)


def _convertToNumeric(key, value):
    integerKeys = [
        "FFEPerWeek",
        "Revenue_1",
        "TransitTime",
        "Distance",
        "Capacity FFE",
        "TC rate daily (fixed Cost)",
        "panamaFee",
        "suezFee",
        "Quantity",
        "capacity",
    ]
    floatKeys = [
        "draft",
        "Draft",
        "minSpeed",
        "maxSpeed",
        "designSpeed",
        "Bunker ton per day at designSpeed",
        "Idle Consumption ton/day",
        "speed",
        "CostPerFULL",
        "CostPerFULLTrnsf",
        "PortCallCostFixed",
        "PortCallCostPerFFE",
    ]
    booleanKeys = ["IsPanama", "IsSuez"]
    if value and key in integerKeys:
        return int(value)
    if value and key in floatKeys:
        return float(value) if value != "NULL" else None
    if value and key in booleanKeys:
        return bool(value)
    return value


def _read_linerlib(instance: str, linerLib: str):
    files: Dict[str, Dict[str, Any]] = {}
    dataDir = os.path.join(linerLib, "data")
    distFile = "dist_dense.csv"
    fleetFile = "fleet_data.csv"
    portFile = "ports.csv"
    okInstancePrefix = ["Demand_", "fleet_", "transittime_revision/Demand_"]
    for instancefile in os.listdir(dataDir):
        if not (
            instancefile.endswith(".csv")
            and (
                any([p in instancefile for p in okInstancePrefix])
                or instancefile in [distFile, fleetFile, portFile]
            )
        ):
            continue
        instanceDemandFile = f"Demand_{instance}.csv"
        instanceDemandRevisedFile = f"transittime_revision/Demand_{instance}.csv"
        instanceFleetFile = f"fleet_{instance}.csv"
        if instance and instancefile not in [
            instanceDemandFile,
            instanceDemandRevisedFile,
            instanceFleetFile,
            distFile,
            fleetFile,
            portFile,
        ]:
            continue
        with open(os.path.join(dataDir, instancefile), "rb") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"), delimiter="\t")
            d: Dict[str, Any] = {k: [] for k in reader.fieldnames}
            for row in reader:
                [d[k].append(_convertToNumeric(k, v)) for k, v in row.items()]
            files[instancefile] = d
    fleet = files[fleetFile]
    del files[fleetFile]
    distance = files[distFile]
    del files[distFile]
    ports = files[portFile]
    del files[portFile]
    name = None
    dataDict = {}
    for k, v in files.items():
        dataType = k[k.rfind("/") + 1 : k.rfind("_")]
        name = k[k.rfind("_") + 1 : k.rfind(".")]
        dataDict[dataType] = v
    return name, dataDict["Demand"], dataDict["fleet"], fleet, distance, ports


def _read_rotations(instance: str, dir: str):
    dataDir = os.path.join(dir, "results/BrouerDesaulniersPisinger2014/")
    instancefile = instance + ".log"
    with open(os.path.join(dataDir, instancefile), "r") as f:
        name = instancefile[: instancefile.rfind(".")]
        rotations = []
        speed = []
        capacities = []
        line = f.readline()
        while line:
            # rotations
            if line.startswith("service"):
                capacityValue = int(f.readline().strip().replace("capacity", ""))
                numVessels = int(f.readline().strip().replace("# vessels ", ""))
                capacities.append(capacityValue * numVessels)
                rotation = []
                portLine = f.readline()
                while portLine:
                    if portLine.startswith(" Butterfly"):
                        portLine = f.readline()
                        continue
                    if portLine == "\n":
                        break
                    portLineArray = portLine.split("\t")
                    portValue = portLineArray[1].strip()
                    rotation.append(portValue)
                    portLine = f.readline()
                rotations.append(rotation)
                speedLine = f.readline()
                speedValue = float(speedLine.strip().replace("speed", ""))
                speed.append(speedValue)
            line = f.readline()
        return name, rotations, speed, capacities


def fetch(instance, dir):
    _download(dir)
    return _read_linerlib(instance, dir)


def fetch_rotations(instance, dir):
    _download(dir)
    return _read_rotations(instance, dir)


class GraphBuilder:
    edgeTranshipmentTime = 3
    edgeLoadTime = 1
    edgeLoadCost = 0

    def __init__(self, data, network):
        (
            self._name,
            self._demand,
            self._fleet,
            self._fleet_data,
            self._distance,
            self._ports,
        ) = data
        self._rotationName, self._rotations, self._speed, self._capacities = network
        self.cost: List[float] = []
        self.transitTime: List[float] = []
        self.capacity: List[int] = []

        self._portExists = sorted(set(p for r in self._rotations for p in r))

        self.demand = self._getDemand()
        self.transitTimeMax = self._getTransitTimeMax()
        self._numK = len(self.demand)
        self.origins = self._originNodes()
        self.destinations = self._destinationNodes()
        self.vertices = self._portCallNodes()
        self.vertices += set(self.origins)
        self.vertices += set(self.destinations)
        self.edges = self._voyageEdges()
        self.edges += self._transhipmentEdges()
        self.edges += self._loadEdges()

    def _odExists(self, k):
        return (
            self._demand["Origin"][k] in self._portExists
            and self._demand["Destination"][k] in self._portExists
        )

    def _getDemand(self):
        return [
            d for k, d in enumerate(self._demand["FFEPerWeek"]) if self._odExists(k)
        ]

    def _getTransitTimeMax(self):
        return [
            d for k, d in enumerate(self._demand["TransitTime"]) if self._odExists(k)
        ]

    def _portCallNodes(self) -> List[str]:
        return sorted(
            set([f"R{i}_{r}" for i, rs in enumerate(self._rotations) for r in rs])
        )

    def _originNodes(self) -> List[str]:
        vertices = [
            f"O_{self._demand['Origin'][i]}"
            for i in range(len(self._demand["Origin"]))
            if self._odExists(i)
        ]
        return vertices

    def _destinationNodes(self) -> List[str]:
        vertices = [
            f"D_{self._demand['Destination'][i]}"
            for i in range(len(self._demand["Destination"]))
            if self._odExists(i)
        ]
        return vertices

    def _voyageEdges(self) -> List[Tuple[str, str]]:
        zipDistance = list(
            zip(self._distance["fromUNLOCODe"], self._distance["ToUNLOCODE"])
        )
        edges = []
        for i, r in enumerate(self._rotations):
            self.cost += [0] * len(r)
            self.capacity += [self._capacities[i]] * len(r)
            for u, v in list(zip(r, r[1:])) + [(r[-1], r[0])]:
                edges.append((f"R{i}_{u}", f"R{i}_{v}"))
                self.transitTime.append(
                    self._distance["Distance"][zipDistance.index((u, v))]
                    / self._speed[i]
                    / 24
                )
        return edges

    def _transhipmentEdges(self) -> List[Tuple[str, str]]:
        portCalls = self._portCallNodes()
        edges = []
        ports = sorted(set([v[v.rfind("_") + 1 :] for v in portCalls]))
        for p in ports:
            calls = [v for v in portCalls if v[v.rfind("_") + 1 :] == p]
            transhipmentPortEdges = [(u, v) for u in calls for v in calls if v != u]
            index = self._ports["UNLocode"].index(p)
            transhipmentCost = int(self._ports["CostPerFULLTrnsf"][index])
            self.cost += [transhipmentCost] * len(transhipmentPortEdges)
            self.transitTime += [self.edgeTranshipmentTime] * len(transhipmentPortEdges)
            self.capacity += [math.inf] * len(transhipmentPortEdges)
            edges += transhipmentPortEdges
        return edges

    def _loadEdges(self) -> List[Tuple[str, str]]:
        edges = []
        for origin in set(self.origins):
            origin = origin.split("_")[1]
            loadDemandEdges = []
            for j, rs in enumerate(self._rotations):
                if origin in rs:
                    loadDemandEdges.append((f"O_{origin}", f"R{j}_{origin}"))
            self.cost += [self.edgeLoadCost] * len(loadDemandEdges)
            self.transitTime += [self.edgeLoadTime] * len(loadDemandEdges)
            self.capacity += [math.inf] * len(loadDemandEdges)
            edges += loadDemandEdges
        for dest in set(self.destinations):
            dest = dest.split("_")[1]
            loadDemandEdges = []
            for j, rs in enumerate(self._rotations):
                if dest in rs:
                    loadDemandEdges.append((f"R{j}_{dest}", f"D_{dest}"))
            self.cost += [self.edgeLoadCost] * len(loadDemandEdges)
            self.transitTime += [self.edgeLoadTime] * len(loadDemandEdges)
            self.capacity += [math.inf] * len(loadDemandEdges)
            edges += loadDemandEdges
        return edges
