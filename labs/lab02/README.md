# Лабораторна робота №2 — варіант 15

**Варіант 15: Аудитор логів використання привілейованих команд (Sudo / Privileged Access).**

## Встановлення
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Структура
```
labs/lab02/
├── main.py      # команди demo та analyze
├── task1.py     # класи User, Admin, Session, AuditLog, UserAccount
├── task2.py     # утиліта аудиту sudo.log
└── data/
    ├── sudo.log             # вхідний журнал sudo
    └── alert_commands.txt   # список небезпечних команд
```
Файли взято з `lab2_data.zip` → `data/data_v15/`.

## Запуск (з кореня репозиторію)
```bash
python -m labs.lab02.main demo
python -m labs.lab02.main analyze --sudo-log labs/lab02/data/sudo.log --alert-commands labs/lab02/data/alert_commands.txt --out-json labs/lab02/data/sudo_audit_report.json
```
Список команд можна передати і напряму: `--alert-commands "nc,nmap,dd"`.

## Параметри `analyze`
| Параметр | Опис |
|---|---|
| `--sudo-log` | шлях до `sudo.log` (обов'язковий) |
| `--alert-commands` | файл зі списком небезпечних команд або список через кому (за замовчуванням: `chmod 777, nc, nmap, dd, /etc/shadow`) |
| `--out-json` | куди зберегти JSON-звіт (необов'язковий) |
| `--log-level` | `DEBUG`, `INFO` (за замовчуванням), `WARNING`, `ERROR` |

## Поведінка при помилках
- Файлу немає → `[ERROR] Файл не знайдено`, код завершення 1.
- Рядок логу має інший формат → `[WARNING]`, рядок пропускається, програма працює далі.
- Не вдалося записати JSON → `[ERROR]`, код завершення 1.

## Перевірка коду
```bash
ruff check .
ruff format --check .
```
