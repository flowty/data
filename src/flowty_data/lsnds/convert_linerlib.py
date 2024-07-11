import sys
import argparse
import gzip
import io
import os
import tempfile
import flowty_data.linerlib.fetch_linerlib as fetch_linerlib
import flowty_data.lsnds.graph_builder as graph_builder


def _convert(data, timeDisc: int, out):
    instanceName, _, _, _, _, _ = data
    # networkName, _, _, _ = network
    builder = graph_builder.GraphBuilder(data, timeDisc)
    scale = 100
    vessels = {name: i for i, name in enumerate(builder.vessels)}
    vessels["_"] = -1
    quantities = builder.quantities
    vertices = {name: i for i, name in enumerate(builder.vertices)}
    # num
    numV = len(builder.vertices)
    numK = len(builder.demand)
    numVessels = len(builder.vessels)
    numR = 1
    # commodities
    O = [vertices[v] for v in builder.origins]
    D = [vertices[v] for v in builder.destinations]
    transitTimeMax = [i * scale for i in builder.transitTimeMax]
    demand = builder.demand
    profit = builder.profit
    # edges
    numE = len(builder.edges)
    lines = [
        "c liner shipping network design and scheduling\n",
        f"c {instanceName}\n",
        "c\n",
        "c id port\n",
    ]
    for name, i in vertices.items():
        lines += [f"c {i} {name}\n"]
    lines += [
        "c\n",
        "c problem vertices edges commodities vessel_types\n",
        f"p lsnds {numV} {numE} {numK} {numVessels}\n",
        "c\n",
        "c origin destination demand profit time_limits\n",
    ]
    for k in range(numK):
        lines += [f"k {O[k]} {D[k]} {demand[k]} {profit[k]} {transitTimeMax[k]}\n"]
    lines += [
        "c\n",
        "c id vessel_type\n",
    ]
    lines += [f"c {v} {name}\n" for v, name in enumerate(builder.vessels)]
    lines += [
        "c\n",
        "c vessel_type quantity\n",
    ]
    for v in range(numVessels):
        lines += [f"v {v} {quantities[v]}\n"]
    lines += [
        "c\n",
        "c vessel_type source target unit_cost fixed_cost capacity time\n",
    ]
    for vessel, source, target, unit_cost, fixed_cost, capacity, time in builder.edges:
        line = f"a {vessels[vessel]} {vertices[source]} {vertices[target]}"
        line += f" {unit_cost}"
        line += f" {fixed_cost}"
        line += f" {capacity}"
        line += f" {time}"
        lines += [line + "\n"]

    filename = os.path.join(out, f"{instanceName}_h{timeDisc}.txt.gz")
    with gzip.open(filename, 'wb') as output:
        with io.TextIOWrapper(output, encoding='utf-8') as encode:
            encode.writelines(lines)


def convert():
    argv = sys.argv[1:]
    # argv.append("--instance")
    # argv.append("Baltic")
    # argv.append("--time")
    # argv.append("12")
    argv.append("--all")
    argv.append("--out")
    argv.append("data/lsnds")

    parser = argparse.ArgumentParser(description="Converts LinerLib data to LSNDS")
    parser.add_argument("--type", help="Converts linerlib data to Flowty format")
    parser.add_argument("--instance", help="Instance name")
    parser.add_argument("--time", help="Time discretization", default=12)
    parser.add_argument("--linerlib", help="place to read linerlib files", default=None)
    parser.add_argument("--out", help="place to put LSNDS files", default=".")
    parser.add_argument(
        "--all",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="convert all",
    )
    args = parser.parse_args(argv)

    allInstances = [
        "Baltic",
        "EuropeAsia",
        "Mediterranean",
        "Pacific",
        "WAF",
        "WorldSmall",
        "WorldLarge",
    ]
    allTimes = [12, 8, 4]
    dataDir = (
        args.linerlib
        if args.linerlib
        else os.path.join(tempfile.gettempdir(), "LINERLIB")
    )
    os.makedirs(args.out, exist_ok=True)

    if args.all:
        for time in allTimes:
            for instance in allInstances:
                data = fetch_linerlib.fetch(instance, dataDir)
                _convert(data, int(time), args.out)
    else:
        data = fetch_linerlib.fetch(args.instance, dataDir)
        _convert(data, int(args.time), args.out)
