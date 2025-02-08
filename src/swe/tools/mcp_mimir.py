
import argparse

from swe.tools.mimir import Mimir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    return parser.parse_args()


def main(args: argparse.Namespace):
    mimir = Mimir()
    work_item = mimir.get_work_item(work_item_id=args.id)
    print(work_item.id)
    print(work_item.title)
    print(work_item.assigned_to)
    print(work_item.description)


if __name__ == "__main__":
    args = parse_args()
    main(args)
