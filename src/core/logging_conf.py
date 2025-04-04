import json
import logging
import os
from logging.handlers import RotatingFileHandler, SysLogHandler

from .configuration import conf

json_formatter = logging.Formatter(
    json.dumps(
        {
            "process_id": "%(process)d",
            "time": "%(asctime)s",
            "level": "%(levelname)-6s",
            "loggerName": "%(name)s",
            "funcName": "%(funcName)s()",
            "line": "%(pathname)s:%(lineno)d",
            "message": "%(message)s",
        },
    )
)

ch: logging.StreamHandler | RotatingFileHandler | SysLogHandler | None = None
if conf.log.handler == "stdout":
    ch = logging.StreamHandler()
    ch.setLevel(logging.NOTSET)
    ch.setFormatter(json_formatter)
elif conf.log.handler == "file":
    if not os.path.exists("/var/log/spacesan"):
        os.mkdir("/var/log/spacesan")
    ch = RotatingFileHandler(
        filename="/var/log/spacesan/spsan.log" if conf.log.path is None else conf.log.path,
        maxBytes=500_000_000,  # 500MB
        backupCount=10,
        encoding="utf8",
    )
    ch.setLevel(logging.NOTSET)
    ch.setFormatter(json_formatter)
elif conf.log.handler == "syslog":
    ch = SysLogHandler(address=("127.0.0.1", 514) if conf.log.path is None else conf.log.path)
    ch.setLevel(logging.NOTSET)
    ch.setFormatter(json_formatter)
else:
    raise Exception
