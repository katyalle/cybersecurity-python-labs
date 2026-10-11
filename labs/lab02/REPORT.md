# Звіт до лабораторної роботи №2 (варіант 15)

**Тема:** Розробка консольних утиліт для задач кібербезпеки
**Варіант 15:** Аудитор логів використання привілейованих команд (Sudo / Privileged Access)

Репозиторій: _(вставте посилання)_  Коміт: _(вставте хеш коміту)_

## 1. Завдання 1: схема взаємодії класів
```
UserAccount ──has-a──► User  ◄──is-a── Admin
     ├────────has-a──► Session
     └────────has-a──► AuditLog ──► список LogRecord (@dataclass)
```
- **Наслідування (Is-A):** `Admin(User)` — адміністратор є користувачем, тому успадковує пароль, email, роль; додає `permissions` і перевизначає `__str__`.
- **Композиція (Has-A):** `UserAccount` містить `User`, `Session`, `AuditLog` — обліковий запис не є сеансом чи журналом, а складається з них.
- **`@dataclass` для запису аудиту:** запис — це просто набір полів (час, користувач, дія); декоратор сам створює `__init__`, `__repr__`, `__eq__`, тож не треба писати їх вручну.
- Пароль зберігається як `pbkdf2_hmac("sha256")` із випадковою сіллю `os.urandom` і порівнюється через `hmac.compare_digest`. Простий `sha256(password)` для справжніх систем не підходить: він швидкий і дозволяє підбір.

Запуск: `python -m labs.lab02.main demo`

## 2. Завдання 2: команда запуску
```bash
python -m labs.lab02.main analyze --sudo-log labs/lab02/data/sudo.log \
  --alert-commands labs/lab02/data/alert_commands.txt \
  --out-json labs/lab02/data/sudo_audit_report.json
```
Вхідні файли: `sudo.log` (12 рядків), `alert_commands.txt` (`chmod 777`, `nc`, `nmap`, `dd`, `/etc/shadow`).

### Результат
```
[INFO] Parsing sudo usage logs from labs/lab02/data/sudo.log...
[INFO] Processed 12 privileged execution entries.

=== Privileged Execution Summary ===
Total Sudo Commands : 12
Root Executions     : 10

=== Suspicious / High-Risk Command Executions ===
[ALERT] User 'carol' executed: 'sudo /usr/bin/chmod 777 /srv/share' on TTY=pts/2
[ALERT] User 'carol' executed: 'sudo /usr/bin/nc -lvp 4444' on TTY=pts/2
[ALERT] User 'carol' executed: 'sudo /usr/bin/nmap -sS 10.0.0.0/24' on TTY=pts/2
[ALERT] User 'dave' executed: 'sudo /usr/bin/dd if=/dev/zero of=/tmp/test.img bs=1M count=10' on TTY=pts/3
[ALERT] User 'dave' executed: 'sudo /usr/bin/vim /etc/shadow' on TTY=pts/3
[ALERT] User 'carol' executed: 'sudo /usr/bin/chmod 777 /tmp/public' on TTY=pts/2
[ALERT] User 'carol' executed: 'sudo /usr/bin/nc 203.0.113.10 9001' on TTY=pts/2

=== Top Sudo Users ===
1. carol : 5 commands (High risk commands: 5)
2. alice : 3 commands (High risk commands: 0)
3. dave : 2 commands (High risk commands: 2)
4. bob : 1 commands (High risk commands: 0)
5. eve : 1 commands (High risk commands: 0)

[WARNING] Знайдено небезпечних команд: 7
[INFO] Privileged command audit saved to labs/lab02/data/sudo_audit_report.json
```

### Пояснення знайдених аномалій
- **carol** — 5 небезпечних команд з 5: `chmod 777` (відкриті права на каталоги, двічі), `nc -lvp 4444` (відкриття порту, що слухає — типова ознака reverse/bind shell), `nc 203.0.113.10 9001` (з'єднання із зовнішньою адресою), `nmap -sS` (сканування мережі). Така послідовність схожа на розвідку і закріплення в мережі.
- **dave** — `dd if=/dev/zero ...` (запис великих даних, потенційно руйнівна команда) і `vim /etc/shadow` (редагування файлу з хешами паролів).
- **alice, bob, eve** — звичайні адміністративні команди, не позначені.
- Усього 12 записів, 10 із них виконано від імені `root`.

## 3. Результати Ruff
```
$ ruff check .
All checks passed!
```
```
$ ruff format --check .
8 files already formatted
```
Під час перевірки Ruff знайшов: правило RUF012 (змінний атрибут класу `ALLOWED_KEYS` — виправлено через `typing.ClassVar`), I001 (неправильний порядок імпортів — виправлено `ruff check --fix`) і зауваження до форматування довгих рядків (виправлено `ruff format`).

## 4. Відповіді на контрольні питання
1. **Інкапсуляція.** Це приховування внутрішніх даних класу та доступ до них через методи. `_x` (protected) — домовленість «не чіпати ззовні», Python цього не забороняє. `__x` (private) — Python змінює ім'я на `_Клас__x` (**name mangling**), тому прямий доступ `obj.__x` ззовні не працює (хоча через `_Клас__x` технічно можна).
2. **`@property`.** Зовні `user.email` виглядає як звичайний атрибут, але всередині є перевірка при записі. Не потрібні `get_email()`/`set_email()`; код коротший і природніший, а інтерфейс класу можна пізніше змінити без зміни коду, що його використовує.
3. **Is-A та Has-A.** `Admin` — різновид користувача (Is-A), тому наслідування. `UserAccount` лише складається з користувача, сеансу й журналу (Has-A) — тому композиція. Композиція гнучкіша: частини можна замінити, і вони не пов'язані жорстко.
4. **`__getitem__`/`__setitem__`.** Дозволяють працювати з об'єктом як зі словником: `account["user"]`. Ми контролюємо дозволені ключі (`KeyError`) і типи значень (`TypeError`), а хеш пароля через ключі не доступний.
5. **`@dataclass`.** Автоматично створює `__init__`, `__repr__`, `__eq__`. Доцільний для класів, які головним чином зберігають дані (запис журналу, результат розбору) — коду менше, ніж у класу, і структура чітка, на відміну від словника, де можна помилитися в назві ключа.
6. **`pathlib`.** Шлях — це об'єкт, а не рядок: `Path("a") / "b"` працює однаково в Windows і Linux, є зручні методи `.exists()`, `.read_text()`, `.mkdir()`, `.suffix`. Менше помилок із роздільниками та конкатенацією рядків.
7. **`Counter` і `defaultdict`.** `Counter` рахує кількість елементів в одному рядку коду та має `most_common()` (у нас — команди за користувачами). `defaultdict` сам створює значення для нового ключа, тому не потрібно перевіряти `if key in dict`. Обидва швидкі й зручні для великих логів.
8. **`argparse`.** Обов'язкові аргументи — `required=True` (у нас `--sudo-log`), прапорці — `action="store_true"`, типи — `type=int`, обмежені значення — `choices=[...]`. Валідація на рівні `argparse` зупиняє програму з зрозумілим повідомленням ще до початку роботи, а не посеред обробки даних.
9. **`logging` замість `print()`.** Є рівні важливості, формат із часом, можна писати у файл і вимикати зайве без правки коду. `DEBUG` — деталі для розробника, `INFO` — звичайний хід роботи, `WARNING` — щось підозріле, але програма працює (знайдено небезпечні команди), `ERROR` — помилка (файл не знайдено), `CRITICAL` — серйозний збій, продовження неможливе.
10. **Помилки Ruff.** RUF012 (змінний атрибут класу без `ClassVar`) — виправлено анотацією; I001 (порядок імпортів) — `ruff check --fix`; форматування довгих рядків — `ruff format`.
