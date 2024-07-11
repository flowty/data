import os
import tempfile
import math
import csv
import io
from typing import Dict, Any, Tuple, List

import flowty_data.rcmcf.fetch_repo as fetch_repo
import flowty_data.linerlib.fetch_linerlib as fetch_linerlib

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


def fetch_rotations(instance, dir):
    fetch_linerlib.download(dir)
    return _read_rotations(instance, dir)


