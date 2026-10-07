import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def caesar_cipher(text: str, shift: int = 3) -> str:
    """Просте шифрування Цезаря для демонстрації 3 завдання."""
    result = ""
    for char in text:
        if char.isalpha():
            start = ord("A") if char.isupper() else ord("a")
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result


def main():
    """Головна функція для завдання 3."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n")

    secret_message = "Cybersecurity Lab 01 Completed"
    encrypted = caesar_cipher(secret_message, shift=15)

    print(f"Вхідне повідомлення: {secret_message}")
    print(f"Зашифроване (Варіант 15): {encrypted}")


if __name__ == "__main__":
    main()