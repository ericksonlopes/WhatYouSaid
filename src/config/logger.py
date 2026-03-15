from src.infrastructure.loggers.std_logger import StdLogger, InterceptHandler

LOG_FORMAT = "{asctime} | {levelname:<8} | {filepath}:{funcName}:{lineno} | {message} | {context}"


class Logger:
    def __init__(self) -> None:
        self._logger = StdLogger(LOG_FORMAT)

    def __getattr__(self, name):
        return getattr(self._logger, name)

    def get_intercept_handler(self):
        return InterceptHandler(self)
