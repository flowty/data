import math
from typing import Tuple, List

class GraphBuilder:
    edgeTranshipmentTime = 3  # NB: This should not be greater than timeDisc
    edgeLoadTime = 1
    edgeLoadCost = 0

    def __init__(self, data, timeDisc):
        (
            self._name,
            self._demand,
            self._fleet,
            self._fleet_data,
            self._distanceDense,
            self._ports,
        ) = data
        self._portsMap = self._getPortsToIndex()
        self.cost: List[float] = []
        self.transitTime: List[float] = []
        self.capacity: List[int] = []
        self.demand = self._getDemand()
        self.profit = self._getProfit()
        self.transitTimeMax = self._getTransitTimeMax()
        self.vessels = self._getVessels()
        self.quantities = self._getQuantities()
        self.origins = self._originNodes()
        self.destinations = self._destinationNodes()
        self.vertices = sorted(set(self.origins))
        self.vertices += sorted(set(self.destinations))
        self.vertices += self._getPortNodes(timeDisc)
        self._usedPorts = set()
        self.edges = self._voyageEdges(timeDisc)
        self.edges += self._loadEdges(timeDisc)
        self._removeUnusedPorts()
        self.edges += self._transhipmentEdges(timeDisc)

    def _getDemand(self):
        return [d for k, d in enumerate(self._demand["FFEPerWeek"])]

    def _getProfit(self):
        profit = []
        for k in range(len(self.demand)):
            revenue = self._demand["Revenue_1"][k]
            origin = self._demand["Origin"][k]
            destination = self._demand["Destination"][k]
            originCostPerFFE = self._ports["PortCallCostPerFFE"][self._portsMap[origin]]
            destinationCostPerFFE = self._ports["PortCallCostPerFFE"][
                self._portsMap[destination]
            ]
            profit.append(revenue - originCostPerFFE - destinationCostPerFFE)
        return profit

    def _getTransitTimeMax(self):
        return [d for k, d in enumerate(self._demand["TransitTime"])]

    def _originNodes(self) -> List[str]:
        return [
            f"O_{self._demand['Origin'][i]}" for i in range(len(self._demand["Origin"]))
        ]

    def _destinationNodes(self) -> List[str]:
        return [
            f"D_{self._demand['Destination'][i]}"
            for i in range(len(self._demand["Destination"]))
        ]

    def _getRegions(self) -> set[str]:
        demandPorts = {
            self._demand["Origin"][i] or self._demand["Destination"][i]
            for i in range(len(self._demand["Origin"]))
        }
        regions = {
            self._ports["D_Region"][i]
            for i in range(len(self._ports["UNLocode"]))
            if self._ports["UNLocode"][i] in demandPorts
        }
        return regions

    def _getPortsToIndex(self):
        regions = self._getRegions()
        return {
            p: i
            for i, (p, r) in enumerate(
                zip(self._ports["UNLocode"], self._ports["D_Region"])
            )
            if r in regions
        }

    def _getVessels(self) -> set[str]:
        return self._fleet["Vessel class"]

    def _getQuantities(self):
        return self._fleet["Quantity"]

    def _getPortNodes(self, timeDisc: int) -> List[str]:
        return [
            f"{p}_{timePoint}"
            for p in sorted(self._portsMap.keys())
            for timePoint in range(0, 7 * 24, timeDisc)
        ]

    def _voyageEdges(self, timeDisc) -> List[Tuple[str, str]]:
        distances = {}
        for i in range(len(self._distanceDense["fromUNLOCODe"])):
            if (
                self._distanceDense["fromUNLOCODe"][i] in self._portsMap.keys()
                and self._distanceDense["ToUNLOCODE"][i] in self._portsMap.keys()
            ):
                distances[
                    (
                        self._distanceDense["fromUNLOCODe"][i],
                        self._distanceDense["ToUNLOCODE"][i],
                    )
                ] = (
                    self._distanceDense["fromUNLOCODe"][i],
                    self._distanceDense["ToUNLOCODE"][i],
                    self._distanceDense["Distance"][i],
                    self._distanceDense["IsPanama"][i],
                    self._distanceDense["IsSuez"][i],
                )
        edges = []
        vesselToIndex = {v: i for i, v in enumerate(self._fleet_data["Vessel class"])}
        # c vessel source target cost capacity time
        for vessel_class in self._fleet["Vessel class"]:
            v = vesselToIndex[vessel_class]
            capacity = self._fleet_data["Capacity FFE"][v]
            dailyCost = self._fleet_data["TC rate daily (fixed Cost)"][v]
            draft = self._fleet_data["draft"][v]
            minSpeed = self._fleet_data["minSpeed"][v]
            maxSpeed = self._fleet_data["maxSpeed"][v]
            designSpeed = self._fleet_data["designSpeed"][v]
            # bunkerTonPerDay
            # idleConsumption
            panamaFee = self._fleet_data["panamaFee"][v]
            suezFee = self._fleet_data["suezFee"][v]
            for fromPort, toPort, distance, isPanama, isSuez in distances.values():
                if (
                    fromPort in self._portsMap.keys()
                    and toPort in self._portsMap.keys()
                    and (isPanama and panamaFee != None or not isPanama)
                ):
                    if (
                        self._ports["Draft"][self._portsMap[fromPort]] < draft
                        or self._ports["Draft"][self._portsMap[toPort]] < draft
                    ):
                        continue
                    self._usedPorts.add(fromPort)
                    self._usedPorts.add(toPort)
                    for timePoint in range(0, 7 * 24, timeDisc):
                        fromTimePort = f"{fromPort}_{timePoint}"
                        prev = ("", "", "", 0.0, 0, 0)
                        for speed in [minSpeed, designSpeed, maxSpeed]:
                            time = (
                                math.ceil(distance / speed / 24 - 0.001 / timeDisc)
                                * timeDisc
                                + max(24, timeDisc)
                            )
                            costPerFULL = self._ports["CostPerFULL"][
                                self._portsMap[toPort]
                            ]
                            costPerFULL = costPerFULL if costPerFULL else 0
                            unit_cost = round(
                                (costPerFULL + self._getFuelCost(v, speed)) / capacity, 2
                            )
                            fixed_cost = round(
                                dailyCost * time / 24
                                + isPanama * (panamaFee if panamaFee else 0)
                                + isSuez * suezFee
                                + self._ports["PortCallCostFixed"][
                                    self._portsMap[toPort]
                                ],
                                2,
                            )
                            toTimePort = f"{toPort}_{(timePoint + time) % 168}"
                            next = (
                                vessel_class,
                                fromTimePort,
                                toTimePort,
                                unit_cost,
                                fixed_cost,
                                capacity,
                                time,
                            )
                            if prev[0] != next[0] or prev[1] != next[1] or prev[2] != next[2] or prev[3] > next[3] or prev[4] > next[4] or prev[5] != next[5] or prev[6] != next[6]:
                                edges.append(next)
                                prev = next
        return edges

    def _getFuelCost(self, vessel, speed):
        fuelPrice = 600.0
        designSpeed = self._fleet_data["designSpeed"][vessel]
        designFuelConsumption = self._fleet_data["Bunker ton per day at designSpeed"][
            vessel
        ]
        idleFuelCost = self._fleet_data["Idle Consumption ton/day"][vessel] * fuelPrice
        return (
            math.pow(speed / designSpeed, 3) * designFuelConsumption * fuelPrice
            + idleFuelCost
        )

    def _transhipmentEdges(self, timeDisc) -> List[Tuple[str, str]]:
        edges = []
        fixed_cost = 0.0
        capacity = 9999999  # math.inf
        time = math.ceil((self.edgeTranshipmentTime - 0.001) / timeDisc) * timeDisc
        for port, p in self._portsMap.items():
            trnsf = self._ports["CostPerFULLTrnsf"][p]
            if trnsf == None:
                continue
            unit_cost = round(trnsf, 2)
            for fromTimePoint in range(0, 7 * 24, timeDisc):
                fromTimePort = f"{port}_{fromTimePoint}"
                toTimePoint = (fromTimePoint + timeDisc) % 168
                toTimePort = f"{port}_{toTimePoint}"
                edges.append(
                    (
                        "_",
                        fromTimePort,
                        toTimePort,
                        unit_cost,
                        fixed_cost,
                        capacity,
                        time,
                    )
                )
        return edges

    def _loadEdges(self, timeDisc) -> List[Tuple[str, str]]:
        edges = []
        unit_cost = 0.0
        fixed_cost = 0.0
        capacity = 9999999  # math.inf
        time = 0
        for origin in sorted(set(self.origins)):
            port = origin.split("_")[1]
            self._usedPorts.add(port)
            for timePoint in range(0, 7 * 24, timeDisc):
                timePort = f"{port}_{timePoint}"
                edges.append(
                    ("_", origin, timePort, unit_cost, fixed_cost, capacity, time)
                )
        for destination in sorted(set(self.destinations)):
            port = destination.split("_")[1]
            self._usedPorts.add(port)
            for timePoint in range(0, 7 * 24, timeDisc):
                timePort = f"{port}_{timePoint}"
                edges.append(
                    ("_", timePort, destination, unit_cost, fixed_cost, capacity, time)
                )
        return edges

    def _removeUnusedPorts(self):
        self.vertices = [
            vertex
            for vertex in self.vertices
            if vertex.split("_")[0] in self._usedPorts
            or vertex.split("_")[1] in self._usedPorts
        ]
        toDelete = [
            port for port in self._portsMap.keys() if port not in self._usedPorts
        ]
        for port in toDelete:
            self._portsMap.pop(port)