"""Завдання 1: користувач, сеанс, аудит і обліковий запис (ООП)."""

import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import ClassVar

ITERATIONS = 100_000  # кількість ітерацій для pbkdf2
SESSION_TIMEOUT_SEC = 900  # час життя сеансу (15 хвилин)

# логін: літера + ще 2..64 символи (разом 3-64), потім @ і домен з крапкою
EMAIL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


def now_utc():
    """Поточний час у UTC."""
    return datetime.now(timezone.utc)


class User:
    """Користувач: пароль зберігається тільки як хеш із сіллю."""

    def __init__(self, username, email, role="user", active=True):
        self.username = username
        self.email = email  # піде через setter (з перевіркою)
        self.role = role
        self.active = active
        self.__password_hash = b""  # приватні атрибути
        self.__password_salt = b""

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or not EMAIL_RE.match(value):
            raise ValueError(f"Некоректний email: {value!r}")
        self._email = value

    def __make_hash(self, password, salt):
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)

    def set_password(self, password):
        self.__password_salt = os.urandom(16)  # випадкова сіль
        self.__password_hash = self.__make_hash(password, self.__password_salt)

    def check_password(self, password):
        new_hash = self.__make_hash(password, self.__password_salt)
        return hmac.compare_digest(new_hash, self.__password_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        state = "активний" if self.active else "заблокований"
        return f"Користувач {self.username} <{self.email}>, роль: {self.role}, {state}"


class Admin(User):
    """Адміністратор — це користувач (наслідування) з додатковими правами."""

    def __init__(self, username, email, permissions=None):
        super().__init__(username, email, role="admin")
        # не ставимо [] як значення за замовчуванням, щоб список не був спільним
        self.permissions = list(permissions) if permissions else []

    def grant_permission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def revoke_permission(self, permission):
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission):
        return permission in self.permissions

    def __str__(self):
        return super().__str__() + f", права: {', '.join(self.permissions) or '—'}"


class Session:
    """Сеанс користувача."""

    def __init__(self, ip, login_time=None, last_activity=None):
        self.ip = ip
        self.login_time = login_time or now_utc()
        self.last_activity = last_activity or self.login_time

    def touch(self):
        """Оновити час останньої активності."""
        self.last_activity = now_utc()

    def is_active(self, timeout_sec):
        if timeout_sec <= 0:
            raise ValueError("timeout_sec має бути більше нуля")
        return now_utc() - self.last_activity <= timedelta(seconds=timeout_sec)


@dataclass
class LogRecord:
    """Один запис журналу (@dataclass сам створює __init__, __repr__, __eq__)."""

    time: datetime
    username: str
    action: str


class AuditLog:
    """Журнал аудиту (паролі сюди не потрапляють)."""

    def __init__(self):
        self.records = []

    def add_log(self, username, action):
        self.records.append(LogRecord(now_utc(), username, action))

    def show_all(self):
        for rec in self.records:
            print(f"{rec.time:%Y-%m-%d %H:%M:%S} UTC | {rec.username} | {rec.action}")


class UserAccount:
    """Обліковий запис = користувач + сеанс + журнал (композиція)."""

    ALLOWED_KEYS: ClassVar[dict] = {"user": User, "session": Session, "audit": AuditLog}

    def __init__(self, user, audit=None):
        self.user = user
        self.session = None
        self.audit = audit or AuditLog()

    def login(self, username, password, ip):
        if not self.user.active or username != self.user.username:
            self.audit.add_log(username, "login_failure")
            return False
        if not self.user.check_password(password):
            self.audit.add_log(username, "login_failure")
            return False
        self.session = Session(ip)
        self.session.touch()
        self.audit.add_log(username, "login_success")
        return True

    def is_authenticated(self):
        if self.session is None:
            return False
        if not self.session.is_active(SESSION_TIMEOUT_SEC):
            return False
        self.session.touch()  # тільки успішна перевірка подовжує сеанс
        return True

    def logout(self):
        if self.session is not None:
            self.session = None
            self.audit.add_log(self.user.username, "logout")

    def __getitem__(self, key):
        if key not in self.ALLOWED_KEYS:
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise KeyError(key)
        if not isinstance(value, self.ALLOWED_KEYS[key]):
            raise TypeError(
                f"Для ключа {key!r} потрібен тип {self.ALLOWED_KEYS[key].__name__}"
            )
        setattr(self, key, value)


def run_demo():
    """Демонстрація роботи класів (викликається командою demo)."""
    print("=== 1. Створення користувача ===")
    user = User("alice", "alice_01@example.com")
    user.set_password("Str0ng_pass!")
    print(user)

    account = UserAccount(user)

    print("\n=== 2. Невдалий та успішний вхід ===")
    print("Невірний пароль:", account.login("alice", "wrong", "10.0.0.5"))
    print("Вірний пароль:  ", account.login("alice", "Str0ng_pass!", "10.0.0.5"))
    print("Автентифікований:", account.is_authenticated())

    print("\n=== 3. Зміна email з валідацією ===")
    user.email = "alice_new@example.org"
    print("Новий email:", user.email)
    try:
        user.email = "1bad@@mail"
    except ValueError as err:
        print("Помилка:", err)

    print("\n=== 4. Права адміністратора ===")
    admin = Admin("root_admin", "admin_user@corp.ua")
    admin.set_password("Adm1n_pass!")
    admin.grant_permission("read_logs")
    admin.grant_permission("manage_users")
    print(admin)
    admin.revoke_permission("read_logs")
    print("has read_logs:", admin.has_permission("read_logs"))
    print("has manage_users:", admin.has_permission("manage_users"))

    print("\n=== 5. Завершення сеансу за таймаутом ===")
    account.session.last_activity -= timedelta(seconds=SESSION_TIMEOUT_SEC + 60)
    print("Автентифікований після таймауту:", account.is_authenticated())

    print("\n=== 6. Повторний вхід і вихід ===")
    account.login("alice", "Str0ng_pass!", "10.0.0.5")
    account.logout()
    print("Автентифікований після logout:", account.is_authenticated())

    print("\n=== 7. __getitem__ / __setitem__ ===")
    print("account['user'] ->", account["user"].username)
    try:
        account["password"]
    except KeyError as err:
        print("KeyError:", err)
    try:
        account["user"] = "рядок"
    except TypeError as err:
        print("TypeError:", err)

    print("\n=== 8. Журнал аудиту ===")
    account.audit.show_all()
