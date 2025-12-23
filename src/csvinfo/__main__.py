import sys
import argparse

from . import CSVTree


def main() -> int:
    
    # pr: parser root
    pr = argparse.ArgumentParser()

    pr.add_argument(
        'csv_file_path'
    )

    args = pr.parse_args()

    CSVTree(csv_file_path=args.csv_file_path)

    return 0



if '__main__' == __name__:
    sys.exit(main())




