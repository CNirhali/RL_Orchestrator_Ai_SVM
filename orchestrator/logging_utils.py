import logging
import sys
from typing import Any, Mapping, Optional


class TaskLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: Mapping[str, Any]):
        extra = dict(self.extra or {})
        kwargs_extra = dict(kwargs.get("extra") or {})
        merged = {**extra, **kwargs_extra}
        kwargs = dict(kwargs)
        kwargs["extra"] = merged
        return msg, kwargs


def configure_logging(level: Optional[str] = None) -> None:
    log_level = (level or "INFO").upper()
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s task_id=%(task_id)s %(message)s",
    )


def get_logger(name: str, task_id: Optional[str] = None) -> logging.LoggerAdapter:
    logger = logging.getLogger(name)
    return TaskLoggerAdapter(logger, {"task_id": task_id or "-"})

