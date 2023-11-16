import sys
import argparse

from flowty_data.mcf import convert_planargrid
from flowty_data.linerlib import convert_linerlib


def main():
    argv = sys.argv[1:]
    # argv.append("--type")
    # argv.append("mcf")
    # argv.append("linerlib")

    parser = argparse.ArgumentParser(
        description="Converts instance data to Flowty format"
    )
    parser.add_argument("--type", help="Converts mcf data to Flowty format")
    args = parser.parse_args(argv)

    if args.type == "mcf":
        return convert_planargrid.convert()
    if args.type == "linerlib":
        return convert_linerlib.convert()

    raise TypeError("Unknown instance type")


if __name__ == "__main__":
    main()
