import re

_PASSWORD_CHECKS = (
    (re.compile(r"[a-z]"), "строчную латинскую букву"),
    (re.compile(r"[A-Z]"), "заглавную латинскую букву"),
    (re.compile(r"\d"), "цифру"),
    (re.compile(r"[^A-Za-z0-9]"), "специальный символ"),
)


def missing_password_requirements(value: str) -> list[str]:
    """Возвращает список несоблюдённых требований к паролю."""
    return [description for pattern, description in _PASSWORD_CHECKS if not pattern.search(value)]


def validate_password_strength(value: str) -> str:
    """Проверяет сложность пароля и возвращает его без изменений."""
    missing = missing_password_requirements(value)
    if missing:
        raise ValueError("Пароль должен содержать " + ", ".join(missing))
    return value
