"""Завдання 2 (варіант 15): аудитор логів sudo."""

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("sudo_audit")

# Один рядок логу, наприклад:
# 2026-09-27T09:20:00+03:00 host01 sudo: carol : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/chmod 777 /srv/share
LINE_RE = re.compile(
    r"^(?P<timestamp>\S+)\s+\S+\s+sudo:\s+(?P<user>\S+)\s+:\s+"
    r"TTY=(?P<tty>\S+)\s+;\s+PWD=(?P<pwd>\S+)\s+;\s+"
    r"USER=(?P<target>\S+)\s+;\s+COMMAND=(?P<command>.+)$"
)

# Небезпечні команди за замовчуванням (якщо не вказано --alert-commands)
DEFAULT_ALERTS = ["chmod 777", "nc", "nmap", "dd", "/etc/shadow"]


@dataclass
class SudoEntry:
    """Один розібраний запис sudo-логу."""

    timestamp: str
    user: str
    tty: str
    pwd: str
    target_user: str
    command: str


def parse_line(line):
    """Розібрати рядок логу. Якщо формат не підходить — повертає None."""
    match = LINE_RE.match(line.strip())
    if match is None:
        return None
    return SudoEntry(
        match["timestamp"],
        match["user"],
        match["tty"],
        match["pwd"],
        match["target"],
        match["command"],
    )


def load_alert_commands(value):
    """--alert-commands: шлях до файлу АБО список через кому."""
    if not value:
        return DEFAULT_ALERTS
    path = Path(value)
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
        return [line.strip() for line in lines if line.strip()]
    return [item.strip() for item in value.split(",") if item.strip()]


def find_risky_pattern(command, patterns):
    """Повертає перший шаблон, що знайдений у команді, або None."""
    for pattern in patterns:
        # (?<!\w) і (?!\w) — щоб "dd" не знаходилось у слові "add"
        regex = r"(?<!\w)" + re.escape(pattern) + r"(?!\w)"
        if re.search(regex, command):
            return pattern
    return None


def analyze(sudo_log, patterns):
    """Головна логіка: читає лог і повертає словник з результатами."""
    entries = []
    bad_lines = 0
    with open(sudo_log, encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            entry = parse_line(line)
            if entry is None:
                bad_lines += 1
                logger.warning("Не вдалося розібрати рядок: %s", line.strip())
            else:
                entries.append(entry)

    users_counter = Counter()  # скільки команд виконав кожен користувач
    risky_counter = Counter()  # скільки небезпечних команд у кожного
    root_count = 0
    risky = []

    for entry in entries:
        users_counter[entry.user] += 1
        if entry.target_user == "root":
            root_count += 1
        pattern = find_risky_pattern(entry.command, patterns)
        if pattern:
            risky_counter[entry.user] += 1
            risky.append({"entry": entry, "pattern": pattern})

    return {
        "entries": entries,
        "bad_lines": bad_lines,
        "root_count": root_count,
        "risky": risky,
        "users_counter": users_counter,
        "risky_counter": risky_counter,
    }


def print_report(result):
    """Виводить звіт у консоль."""
    print()
    print("=== Privileged Execution Summary ===")
    print(f"Total Sudo Commands : {len(result['entries'])}")
    print(f"Root Executions     : {result['root_count']}")

    print()
    print("=== Suspicious / High-Risk Command Executions ===")
    if not result["risky"]:
        print("Підозрілих команд не знайдено.")
    for item in result["risky"]:
        e = item["entry"]
        print(f"[ALERT] User '{e.user}' executed: 'sudo {e.command}' on TTY={e.tty}")

    print()
    print("=== Top Sudo Users ===")
    for place, (user, count) in enumerate(result["users_counter"].most_common(), 1):
        risky_n = result["risky_counter"][user]
        print(f"{place}. {user} : {count} commands (High risk commands: {risky_n})")
    print()


def save_json(result, out_json, sudo_log):
    """Зберігає результати аудиту у JSON-файл."""
    data = {
        "source_file": str(sudo_log),
        "total_commands": len(result["entries"]),
        "root_executions": result["root_count"],
        "unparsed_lines": result["bad_lines"],
        "high_risk_commands": [
            {
                "timestamp": item["entry"].timestamp,
                "user": item["entry"].user,
                "tty": item["entry"].tty,
                "target_user": item["entry"].target_user,
                "command": item["entry"].command,
                "matched_pattern": item["pattern"],
            }
            for item in result["risky"]
        ],
        "commands_per_user": dict(result["users_counter"]),
        "high_risk_per_user": dict(result["risky_counter"]),
    }
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def add_arguments(parser):
    """Додає аргументи командного рядка до парсера."""
    parser.add_argument("--sudo-log", required=True, help="шлях до sudo.log")
    parser.add_argument(
        "--alert-commands",
        help="файл зі списком небезпечних команд або список через кому",
    )
    parser.add_argument("--out-json", help="куди зберегти JSON-звіт")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="рівень логування (за замовчуванням INFO)",
    )


def run(args):
    """Запуск утиліти. Повертає 0 при успіху і 1 при помилці."""
    logging.basicConfig(level=args.log_level, format="[%(levelname)s] %(message)s")

    sudo_log = Path(args.sudo_log)
    if not sudo_log.is_file():
        logger.error("Файл не знайдено: %s", sudo_log)
        return 1

    try:
        patterns = load_alert_commands(args.alert_commands)
        logger.info("Parsing sudo usage logs from %s...", sudo_log)
        result = analyze(sudo_log, patterns)
    except (OSError, UnicodeDecodeError) as err:
        logger.error("Помилка читання файлу: %s", err)
        return 1

    logger.info("Processed %d privileged execution entries.", len(result["entries"]))
    print_report(result)

    if result["risky"]:
        logger.warning("Знайдено небезпечних команд: %d", len(result["risky"]))

    if args.out_json:
        try:
            save_json(result, args.out_json, sudo_log)
        except OSError as err:
            logger.error("Не вдалося зберегти звіт: %s", err)
            return 1
        logger.info("Privileged command audit saved to %s", args.out_json)
    return 0
