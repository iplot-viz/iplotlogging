"""Unit tests for ``get_file_handler``.

The file handler is the rotating-on-disk path for IDV logs. The lookup
order for the destination is:

- ``IPLOT_LOG_PATH`` env var, falling back to ``~/.local/1Dtool``;
- ``IPLOT_LOG_FILENAME`` env var, falling back to a host/pid-stamped name;
- the resulting directory ``<base>/logs/`` is created if missing.

The handler also gets the two custom filters and a formatter that
includes hostname/username — those are what makes the log lines
traceable across the cluster, so the wiring matters.
"""

import logging
import os
import unittest
import unittest.mock
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from iplotLogging.setupLogger import (HostnameFilter, UserFilter,
                                      get_file_handler)


class GetFileHandlerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = Path(self._make_tmp_dir())

    def tearDown(self):
        # Best-effort cleanup; rotating handlers may keep the file open.
        for fh in list(logging.getLogger().handlers):
            if isinstance(fh, TimedRotatingFileHandler):
                fh.close()

    def _make_tmp_dir(self) -> str:
        import tempfile
        return tempfile.mkdtemp(prefix="iplotlogging_test_")

    def _patched_env(self, **overrides):
        return unittest.mock.patch.dict("os.environ", overrides, clear=False)

    def test_returns_timed_rotating_file_handler(self):
        with self._patched_env(IPLOT_LOG_PATH=str(self._tmp)):
            handler = get_file_handler()
            try:
                self.assertIsInstance(handler, TimedRotatingFileHandler)
            finally:
                handler.close()

    def test_creates_logs_subdirectory_when_missing(self):
        logs_dir = self._tmp / "logs"
        self.assertFalse(logs_dir.exists())

        with self._patched_env(IPLOT_LOG_PATH=str(self._tmp)):
            handler = get_file_handler()
            handler.close()

        self.assertTrue(logs_dir.is_dir())

    def test_respects_filename_env_var(self):
        with self._patched_env(
                IPLOT_LOG_PATH=str(self._tmp),
                IPLOT_LOG_FILENAME="custom_test.log"):
            handler = get_file_handler()
            try:
                self.assertEqual(
                    os.path.basename(handler.baseFilename), "custom_test.log")
            finally:
                handler.close()

    def test_attaches_hostname_and_user_filters(self):
        with self._patched_env(IPLOT_LOG_PATH=str(self._tmp)):
            handler = get_file_handler()
            try:
                filter_types = {type(f) for f in handler.filters}
                self.assertIn(HostnameFilter, filter_types)
                self.assertIn(UserFilter, filter_types)
            finally:
                handler.close()

    def test_formatter_includes_hostname_and_username_fields(self):
        with self._patched_env(IPLOT_LOG_PATH=str(self._tmp)):
            handler = get_file_handler()
            try:
                fmt = handler.formatter._fmt
                self.assertIn("%(hostname)s", fmt)
                self.assertIn("%(username)s", fmt)
            finally:
                handler.close()


if __name__ == "__main__":
    unittest.main()
