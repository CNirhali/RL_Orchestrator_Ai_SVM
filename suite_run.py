import argparse
import json

from orchestrator.test_suite_graph import create_best_suite


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create and optionally run a LangGraph-selected test suite."
    )
    parser.add_argument(
        "--changed-path",
        action="append",
        default=[],
        help="Changed path to include in suite selection (repeatable).",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run selected commands in addition to planning.",
    )
    args = parser.parse_args()

    result = create_best_suite(changed_paths=args.changed_path, run_commands=args.run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

