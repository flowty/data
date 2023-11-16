import sys
import argparse

from flowty_data.mcf import convert_planargrid


def main():
    argv = sys.argv[1:]
    # argv.append("--type")
    # argv.append("mcf")

    parser = argparse.ArgumentParser(
        description="Converts instance data to Flowty format"
    )
    parser.add_argument("--type", help="Converts mcf data to Flowty format")
    args = parser.parse_args(argv)

    if args.type == "mcf":
        return convert_planargrid.convert()

    raise TypeError("Unknown instance type")


if __name__ == "__main__":
    main()
