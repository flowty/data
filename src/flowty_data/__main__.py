import sys
import argparse

from flowty_data.mcf import convert_planargrid
from flowty_data.linerlib import convert_linerlib
from flowty_data.vrptw import convert_solomonhg


def main():
    argv = sys.argv[1:]
    # argv.append("--type")
    # argv.append("mcf")
    # argv.append("linerlib")
    # argv.append("vrptw")

    parser = argparse.ArgumentParser(
        description="Converts instance data to Flowty format"
    )
    parser.add_argument("--type", help="Converts mcf data to Flowty format")
    args = parser.parse_args(argv)

    if args.type == "mcf":
        return convert_planargrid.convert()
    if args.type == "linerlib":
        return convert_linerlib.convert()
    if args.type == "vrptw":
        return convert_solomonhg.convert()

    raise TypeError("Unknown instance type")


if __name__ == "__main__":
    main()
