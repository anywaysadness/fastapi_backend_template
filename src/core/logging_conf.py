import logging

from colorlog import ColoredFormatter


def configure_logging(level=logging.INFO):
    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(level)

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()

    # Определяем цветной форматтер
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s.%(msecs)03d] %(module)30s:%(lineno)-4d %(levelname)7s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",  # Голубой для DEBUG
            "INFO": "green",  # Зеленый для INFO
            "WARNING": "yellow",  # Желтый для WARNING
            "ERROR": "red",  # Красный для ERROR
            "CRITICAL": "bold_red",  # Жирный красный для CRITICAL
        },
        secondary_log_colors={},
        style="%",
    )

    # Применяем форматтер к обработчику
    console_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(console_handler)
