import sys
import argparse

from flowty_data.fcmcf import convert_canad
from flowty_data.lsnds import convert_linerlib as convert_lsnds_linerlib
from flowty_data.mcf import convert_planargrid
from flowty_data.rcmcf import convert_linerlib as convert_rcmcf_linerlib
from flowty_data.smptsp import convert_ptask
from flowty_data.vrptw import convert_solomonhg
from flowty_data.pdptw import convert_aabbccdd


def main():
    argv = sys.argv[1:]
    argv.append("--type")
    # argv.append("fcmcf")
    # argv.append("lsnds")
    # argv.append("mcf")
    argv.append("pdptw")
    # argv.append("rcmcf")
    # argv.append("smptsp")
    # argv.append("vrptw")

    parser = argparse.ArgumentParser(
        description="Converts instance data to Flowty format"
    )
    parser.add_argument("--type", help="Converts data to Flowty format")
    args = parser.parse_args(argv)

    if args.type == "fcmcf":
        return convert_canad.convert()
    if args.type == "lsnds":
        return convert_lsnds_linerlib.convert()
    if args.type == "mcf":
        return convert_planargrid.convert()
    if args.type == "pdptw":
        return convert_aabbccdd.convert()
    if args.type == "rcmcf":
        return convert_rcmcf_linerlib.convert()
    if args.type == "smptsp":
        return convert_ptask.convert()
    if args.type == "vrptw":
        return convert_solomonhg.convert()

    raise TypeError("Unknown instance type")


if __name__ == "__main__":
    main()
