"""Головний файл для запуску всіх завдань ЛР1."""

from labs.lab01.task1 import analyze_passwords
from labs.lab01.task2 import check_access
from labs.lab01.task3 import main as run_task3


def main() -> None:
    print("=" * 60)
    print("ЗАПУСК ЗАВДАННЯ 1")
    print("=" * 60)
    analyze_passwords()

    print("\n" + "=" * 60)
    print("ЗАПУСК ЗАВДАННЯ 2")
    print("=" * 60)
    check_access()

    print("\n" + "=" * 60)
    print("ЗАПУСК ЗАВДАННЯ 3")
    print("=" * 60)
    run_task3()


if __name__ == "__main__":
    main()