import logging
import os
import socket

class ExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        try:
            hostname = socket.gethostname()
            record.ip =  socket.gethostbyname(hostname)
        except Exception:
            record.ip = "unknown"

        standard_attrs = logging.LogRecord(
            name="",
            level=0,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None,
        ).__dict__.keys()

        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in standard_attrs and k != "ip"
        }

        record.extras = extras if extras else "none"

        return super().format(record)


def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    handler = logging.StreamHandler()

    formatter = ExtraFormatter(
        fmt=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "%(ip)s | %(message)s | extras=%(extras)s"
        )
    )

    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
