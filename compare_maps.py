import json
import argparse
from deepdiff import DeepDiff

"""
Debug Script
Export Editable Map and Playable Map, convert latter using main.py, run this using paths to both Editable Map and 
conversion result. Ideally the result will be "{}" (an empty dict). Anything else might (might! Sometimes 
different list orders get marked or the difference is inconsequential) indicate a mistake in main.py
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("real", metavar='Realfile Path',
                        type=str, help='- Absolute path to proper *.pumap file')
    parser.add_argument("compare", metavar='Comparefile Path',
                        type=str, help='- Absolute path to generated *.pumap file')
    args = parser.parse_args()

    real_path = args.real
    compare_path = args.compare

    with open(real_path) as real_file:
        with open(compare_path) as compare_file:
            real_obj = json.load(real_file)
            compare_obj = json.load(compare_file)

            print(DeepDiff(real_obj, compare_obj, ignore_order=True))


if __name__ == '__main__':
    main()
