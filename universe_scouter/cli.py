# universe_scouter/cli.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import argparse
from universe_scouter.explorers.equity_explorer import get_equity_candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--classes", default="equity", help="Comma-separated asset classes")
    parser.add_argument("--limit", type=int, default=250)
    args = parser.parse_args()

    asset_classes = [c.strip() for c in args.classes.split(",")]

    all_assets = []

    if "equity" in asset_classes:
        df = get_equity_candidates(limit=args.limit)
        all_assets.append(df)

    # todo: bond, fut, opt

    combined = pd.concat(all_assets, ignore_index=True)
    print(combined.head())

if __name__ == "__main__":
    main()
