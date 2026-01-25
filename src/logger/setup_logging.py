import logging
import os


class ExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        standard_attrs = logging.LogRecord(
            name="",
            level=0,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None,
        ).__dict__.keys()

        extras = {k: v for k, v in record.__dict__.items() if k not in standard_attrs}

        record.extras = extras if extras else "N/A"

        return super().format(record)


def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    handler = logging.StreamHandler()

    formatter = ExtraFormatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s | extras=%(extras)s"
    )

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)
