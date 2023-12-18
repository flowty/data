import sys
import argparse
import enum
import os
import tempfile
import flowty_data.rcmcf.fetch_linerlib as fetch_linerlib
import flowty_data.rcmcf.fetch_flow_first_paper as fetch_flow_first_paper


def _convert(data, network, out):
    instanceName, _, _, _, _, _ = data
    networkName, _, _, _ = network
    builder = fetch_linerlib.GraphBuilder(data, network)
    scale = 100
    vertices = {name: i for i, name in enumerate(builder.vertices)}
    # num
    numV = len(builder.vertices)
    numK = len(builder.demand)
    numR = 1
    # commodities
    O = [vertices[v] for v in builder.origins]
    D = [vertices[v] for v in builder.destinations]
    transitTimeMax = [i * scale for i in builder.transitTimeMax]
    demand = builder.demand
    # edges
    E = []
    costs = []
    times = []
    capacities = []
    ubCapacity = sum(demand)
    for i, (source, target) in enumerate(builder.edges):
        edge = (vertices[source], vertices[target])
        index = None
        if edge in E:
            index = E.index(edge)
        capacity = (
            builder.capacity[i] if builder.capacity[i] != float("inf") else ubCapacity
        )
        if index:
            capacities[index] += capacity
            capacities[index] = min(capacities[index], ubCapacity)
            continue
        E.append(edge)
        costs.append(builder.cost[i])
        times.append(round(builder.transitTime[i] * scale))
        capacities.append(capacity)
    numE = len(E)
    lines = [
        "c resource constrained multi commodity flow\n",
        f"c {instanceName}\n",
        f"c linerlib_networkname {networkName}\n",
        "c\n",
        "c id type|name\n",
    ]
    for name, i in vertices.items():
        lines += [f"c {i} {name}\n"]
    lines += [
        "c\n",
        "c problem vertices edges commodities resources\n",
        f"p rcmcf {numV} {numE} {numK} {numR}\n",
        "c\n",
        "c origin destination demand resource_limits\n",
    ]
    for k in range(numK):
        lines += [f"k {O[k]} {D[k]} {demand[k]} {transitTimeMax[k]}\n"]
    lines += ["c\n", "c source target cost capacity resource_consumptions\n"]
    for i, edge in enumerate(E):
        line = f"a {edge[0]} {edge[1]}"
        line += f" {costs[i]}"
        line += f" {capacities[i]}"
        line += f" {times[i]}"
        lines += [line + "\n"]

    filename = os.path.join(out, f"{networkName}.txt")
    with open(filename, "w") as f:
        f.writelines(lines)


def convert():
    argv = sys.argv[1:]
    # argv.append("--instance")
    # argv.append("Baltic")
    # argv.append("--network")
    # argv.append("Baltic_best_base")
    # argv.append("--linerlib")
    # argv.append("/tmp/LINERLIB")
    # argv.append("--networkDir")
    # argv.append("/tmp/LINERLIB")
    # argv.append("/tmp/flow-first-route-next-heuristic-shipping-network-design")
    argv.append("--out")
    argv.append("data/rcmcf")
    argv.append("--all")

    parser = argparse.ArgumentParser(description="Converts linerlib data to rcmcf")
    parser.add_argument("--type", help="Converts linerlib data to Flowty format")
    parser.add_argument("--instance", help="instance name")
    parser.add_argument("--network", help="network name")
    parser.add_argument("--linerlib", help="place to read linerlib files", default=None)
    parser.add_argument(
        "--networkDir", help="place to read network rotation files", default=None
    )
    parser.add_argument("--out", help="place to put rcmcf files", default=".")
    parser.add_argument(
        "--all",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="convert all",
    )
    args = parser.parse_args(argv)

    networkDirs = [
        os.path.join(tempfile.gettempdir(), "LINERLIB"),
        os.path.join(
            tempfile.gettempdir(),
            "flow-first-route-next-heuristic-shipping-network-design",
        ),
    ]

    instancesLinerLib = [
        ("Baltic", "Baltic_best_base"),
        ("Baltic", "Baltic_best_high_32766_3"),
        ("Baltic", "Baltic_best_low_30827_3"),
        ("WAF", "WAF_base_best"),
        ("WAF", "WAF_high_best_pid_21672_3"),
        ("WAF", "WAF_low_best_16089_10"),
        ("Mediterranean", "Med_base_best"),
        ("Mediterranean", "Med_high_best_5840_1"),
        ("Mediterranean", "Med_low_best_12808_11"),
        ("Pacific", "Pacific_base_best"),
        ("Pacific", "Pacific_28043_5_low_best"),
        ("Pacific", "Pacific_high_best_30600_4"),
        ("WorldSmall", "WorldSmall_Best_Base"),
        ("WorldSmall", "WorldSmall_high_best_12848_1"),
        ("WorldSmall", "WorldSmall_pid_4953_15_best_low"),
        ("EuropeAsia", "EuropeAsia_pid_26674_12"),
        ("EuropeAsia", "EuropeAsia_pid_824_4_best_high"),
        ("EuropeAsia", "EuropeAsia_pid_26999_11_low_best"),
    ]
    instancesFirstFlow = [
        ("Baltic", "Baltic-All-10"),
        ("WAF", "WAF-All-2"),
        ("Mediterranean", "Mediterranean-All-3"),
        ("Pacific", "Pacific-All-3"),
        ("WorldSmall", "WorldSmall-All-5"),
        ("EuropeAsia", "EuropeAsia-All-2"),
        ("WorldLarge", "WorldLarge-All-5"),
    ]

    os.makedirs(args.out, exist_ok=True)
    dataDir = (
        args.linerlib
        if args.linerlib
        else os.path.join(tempfile.gettempdir(), "LINERLIB")
    )
    networkDirs = [args.networkDir] if args.networkDir else networkDirs
    for networkDir in networkDirs:
        instances = None
        rotations_func = None
        if "LINERLIB" in networkDir:
            rotations_func = fetch_linerlib.fetch_rotations
            instances = instancesLinerLib
        elif "flow-first-route-next-heuristic-shipping-network-design" in networkDir:
            rotations_func = fetch_flow_first_paper.fetch_rotations
            instances = instancesFirstFlow

        if args.all:
            for instance, networkName in instances:
                data = fetch_linerlib.fetch(instance, dataDir)
                network = rotations_func(networkName, networkDir)
                _convert(data, network, args.out)
        else:
            data = fetch_linerlib.fetch(args.instance, dataDir)
            network = rotations_func(args.network, networkDir)
            _convert(data, network, args.out)
