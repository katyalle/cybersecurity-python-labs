"""Завдання 2: Багаторівнева система контролю доступу (Варіант 15)."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER  # noqa: E402

users = {
    "quantum_researcher": {
        "role": "quantum_security",
        "clearance": 4,
        "department": "Quantum Research",
        "active": True,
    },
    "post_quantum_dev": {
        "role": "pq_cryptographer",
        "clearance": 4,
        "department": "Post-Quantum",
        "active": True,
    },
    "network_security": {
        "role": "network_security",
        "clearance": 3,
        "department": "Network Security",
        "active": True,
    },
    "crypto_intern": {
        "role": "crypto_intern",
        "clearance": 1,
        "department": "Internship",
        "active": True,
    },
    "quantum_sim": {
        "role": "simulator",
        "clearance": 2,
        "department": "Simulation",
        "active": False,
    },
}

resources = [
    ("quantum_algorithms", 4),
    ("pq_implementations", 4),
    ("network_protocols", 3),
    ("learning_materials", 1),
    ("quantum_keys", 4),
    ("educational_content", 1),
    ("hybrid_systems", 3),
    ("quantum_computers", 4),
    ("crypto_libraries", 2),
    ("tutorials", 1),
]

security_levels = (
    "Educational",
    "Research",
    "Classified Research",
    "Quantum Secure",
)

blocked_users = {"quantum_sim", "quantum_attack", "algorithm_theft"}


def check_access() -> None:
    """Перевіряє права доступу користувачів до ресурсів."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n")

    print("=== СПИСОК РЕСУРСІВ ТА РІВНІВ БЕЗПЕКИ ===")
    for res_name, level_code in resources:
        text_level = security_levels[level_code - 1]
        print(f"Ресурс: {res_name:<22} | Рівень: {text_level}")
    print("\n" + "=" * 55 + "\n")

    test_users = list(users.keys()) + ["non_existent_user", "quantum_attack"]

    print("=== РЕЗУЛЬТАТИ ПЕРЕВІРКИ ДОСТУПУ ===")
    for username in test_users:
        for res_name, res_level in resources:
            if username not in users:
                status, reason = "DENY", "User not found"
            elif username in blocked_users:
                status, reason = "DENY", "User is blocked"
            elif not users[username]["active"]:
                status, reason = "DENY", "Account inactive"
            elif users[username]["clearance"] >= res_level:
                status, reason = "ALLOW", ""
            else:
                status, reason = "DENY", "Insufficient clearance"

            output = f"user=[{username}] resource=[{res_name}] -> {status}"
            if reason:
                output += f" ({reason})"
            print(output)


if __name__ == "__main__":
    check_access()