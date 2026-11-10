"""Run the full benchmark, print the Markdown report, write MD + JSON to --out."""
import argparse
import os

from e2ebench.benchmark import run_benchmark, to_json, to_markdown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out", help="directory for report.md/report.json")
    args = ap.parse_args()
    result = run_benchmark()
    md = to_markdown(result)
    print(md)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "report.md"), "w") as f:
        f.write(md)
    with open(os.path.join(args.out, "report.json"), "w") as f:
        f.write(to_json(result))
    print("Wrote %s/report.md and %s/report.json" % (args.out, args.out))


if __name__ == "__main__":
    main()

