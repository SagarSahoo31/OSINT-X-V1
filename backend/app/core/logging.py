"""Structured logging configuration with security sanitization for OSINT-X."""

import logging
import re
import sys
from typing import Any


class SensitiveDataFilter(logging.Filter):
    """Filters log messages and record arguments to redact sensitive strings."""

    SENSITIVE_PATTERNS = [
        (re.compile(r"(password|passwd|secret|token|api[_-]?key|bearer)\s*[:=]\s*([^\s,;]+)", re.IGNORECASE), r"\1=******"),
        (re.compile(r"(postgres://|postgresql(\+\w+)?://)([^:]+):([^@]+)@", re.IGNORECASE), r"\1\3:******@"),
        (re.compile(r"(bolt://)([^:]+):([^@]+)@", re.IGNORECASE), r"\1\2:******@"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, repl in self.SENSITIVE_PATTERNS:
                record.msg = pattern.sub(repl, record.msg)
        if record.args:
            if isinstance(record.args, dict):
                sanitized_args = {}
                for k, v in record.args.items():
                    if any(s in str(k).lower() for s in ["password", "secret", "token", "key"]):
                        sanitized_args[k] = "******"
                    else:
                        sanitized_args[k] = v
                record.args = sanitized_args
            elif isinstance(record.args, tuple):
                record.args = tuple("******" if any(s in str(a).lower() for s in ["password", "secret"]) else a for a in record.args)
        return True


def setup_logging(log_level: str = "INFO", app_env: str = "development") -> None:
    """Configures application-wide structured logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())

    root_logger.addHandler(console_handler)

    # Adjust verbosity of third-party noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


logger = logging.getLogger("osintx")
