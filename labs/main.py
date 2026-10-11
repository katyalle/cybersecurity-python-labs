"""Точка входу: python -m labs.lab02.main demo | analyze ..."""

import argparse

from labs.lab02 import task1, task2


def main():
    parser = argparse.ArgumentParser(description="Лабораторна робота №2")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo", help="демонстрація класів із завдання 1")
    analyze_parser = subparsers.add_parser(
        "analyze", help="аудит sudo.log (завдання 2)"
    )
    task2.add_arguments(analyze_parser)

    args = parser.parse_args()
    if args.command == "demo":
        task1.run_demo()
        return 0
    return task2.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
