import os
import tempfile
import math
import csv
import io
from typing import Dict, Any, Tuple, List

import flowty_data.rcmcf.fetch_repo as fetch_repo


def download(dir):
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
    if key in integerKeys:
        return int(value) if value != "NULL" and value != "" else None
    if key in floatKeys:
        return float(value) if value != "NULL" and value != "" else None
    if key in booleanKeys:
        return bool(int(value)) if value != "NULL" and value != "" else None
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

def fetch(instance, dir):
    download(dir)
    return _read_linerlib(instance, dir)

