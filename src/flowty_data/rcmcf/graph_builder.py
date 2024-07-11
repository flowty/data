import math
from typing import Tuple, List


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
        self.vertices += sorted(set(self.origins))
        self.vertices += sorted(set(self.destinations))
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
