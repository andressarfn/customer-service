from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from types import TracebackType
from loguru import logger
import orjson

from src.infrastructure.config.settings import settings


@dataclass
class RecordException:
    type: BaseException | None = None
    value: BaseException | None = None
    traceback: TracebackType | None = None


@dataclass
class RecordFile:
    name: str
    path: str


@dataclass
class RecordLevel:
    name: str
    no: int
    icon: str


@dataclass
class RecordMultiprocess:
    id: int
    name: str


@dataclass
class MessageRecord:
    name: str
    module: str
    function: str
    line: int
    message: str
    time: datetime
    elapsed: timedelta
    file: RecordFile
    level: RecordLevel
    thread: RecordMultiprocess
    process: RecordMultiprocess
    extra: dict | None = None
    exception: RecordException | None = None


@dataclass
class SerializedMessageRecord(MessageRecord):
    SEVERITY_MAP = {
        "TRACE": "DEBUG",
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "SUCCESS": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }

    def __str__(self) -> str:
        row = {
            "name": self.name,
            "module": self.module,
            "function": self.function,
            "line": self.line,
            "message": str(self.message),
            "time": self.time.isoformat(),
            "file": self.file.name,
            "level": self.level.name,
            "thread": self.thread.id,
            "process": self.process.id,
            "exception": str(self.exception),
            "extra": self.extra,
            "severity": self.SEVERITY_MAP.get(self.level.name, "INFO"),
        }
        return orjson.dumps(row).decode()


@dataclass
class UnserializedMessageRecord(MessageRecord):
    def __str__(self):
        row = (
            f"{self.time.isoformat()} | {self.level.name} | "
            f"{self.module}.{self.function}:{self.line} | {self.message} | "
            f"{self.process.id}:{self.thread.id} | {self.message}"
        )

        if self.extra:
            row += " |"
            for key, value in self.extra.items():
                row += f" {key}={value} "
        return row


class AppLoggerFactory:
    def __init__(self, serialize: bool = True, level: str = "INFO"):
        self.serialize = serialize
        self.level = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)

    def setup(self) -> None:
        print("Setting up logger...")
        self._setup_logger()

    def _setup_logger(self) -> None:
        logger.remove()

        sink = self._serialized_sink
        if not self.serialize:
            sink = self._unserialized_sink
        logger.add(sink=sink, level=self.level)

    def _unserialized_sink(self, message: dict) -> None:
        print(UnserializedMessageRecord(**message.record), flush=True)

    def _serialized_sink(self, message: dict) -> None:
        print(SerializedMessageRecord(**message.record), flush=True)


AppLoggerFactory(settings.SERIALIZE_LOGS, settings.LOG_LEVEL).setup()
