"""Unit tests for ``get_logger`` — the main public entry point.

``get_logger`` is what every IDV component calls to obtain a Logger.
It must:
- return a real ``logging.Logger`` keyed by name (so multiple modules
  share the same logger when they pass the same name);
- honour the ``level`` argument over ``IPLOT_LOG_LEVEL`` over the
  INFO default;
- attach both the rotating file handler and a stdout stream handler
  so logs land on disk and on the console at the same time.
"""

import logging
import os
import unittest
import unittest.mock
import uuid

from iplotLogging.setupLogger import FileHandlerIplot, get_logger


def _unique_name(prefix: str = "test_logger") -> str:
    """Each test needs a fresh logger name. ``logging.getLogger`` caches
    by name, so reusing a name leaks state between tests."""
    return f"{prefix}_{uuid.uuid4().hex}"


class GetLoggerReturnsLoggerTest(unittest.TestCase):
    def test_returns_logger_instance_with_given_name(self):
        name = _unique_name()
        logger = get_logger(name)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, name)


class GetLoggerLevelResolutionTest(unittest.TestCase):
    def test_explicit_level_argument_overrides_environment(self):
        with unittest.mock.patch.dict(
                "os.environ", {"IPLOT_LOG_LEVEL": "ERROR"}, clear=False):
            logger = get_logger(_unique_name(), level="DEBUG")
            self.assertEqual(logger.level, logging.DEBUG)

    def test_falls_back_to_environment_when_no_argument(self):
        with unittest.mock.patch.dict(
                "os.environ", {"IPLOT_LOG_LEVEL": "WARNING"}, clear=False):
            logger = get_logger(_unique_name())
            self.assertEqual(logger.level, logging.WARNING)

    def test_falls_back_to_info_when_neither_is_set(self):
        env = {k: v for k, v in os.environ.items() if k != "IPLOT_LOG_LEVEL"}
        with unittest.mock.patch.dict("os.environ", env, clear=True):
            logger = get_logger(_unique_name())
            self.assertEqual(logger.level, logging.INFO)


class GetLoggerHandlersTest(unittest.TestCase):
    def test_logger_has_file_handler_attached(self):
        """The shared rotating file handler must be wired up so messages
        reach the disk log."""
        logger = get_logger(_unique_name())
        self.assertIn(FileHandlerIplot.fhandler, logger.handlers)

    def test_logger_has_stream_handler_attached(self):
        """Stdout output is what the user sees in the terminal."""
        logger = get_logger(_unique_name())
        stream_handlers = [h for h in logger.handlers
                           if isinstance(h, logging.StreamHandler)
                           and not isinstance(
                                h, logging.handlers.TimedRotatingFileHandler)]
        self.assertTrue(stream_handlers,
                        "expected at least one StreamHandler on the logger")


if __name__ == "__main__":
    unittest.main()
