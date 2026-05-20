"""Unit tests for the log-rotation helpers.

``delete_older_files`` is what keeps ``~/.local/1Dtool/logs`` and
``~/.local/1Dtool/dumps`` from growing forever. Its contract is small
but easy to break:

- the path may not exist yet — silent no-op;
- the five most recent files survive even if older than the day limit
  (``files[:-5]`` floor);
- files older than ``days`` are removed, anything fresher is kept;
- ``PermissionError`` while deleting is logged but never propagated.

``delete_older_logs`` and ``delete_older_dumps`` are thin wrappers that
must point at the right subdirectory and respect ``IPLOT_LOG_LIMIT``.
"""

import logging
import os
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

from iplotLogging.setupLogger import (delete_older_dumps, delete_older_files,
                                      delete_older_logs)


def _silent_logger() -> logging.Logger:
    """A logger that never raises and produces no output during tests."""
    logger = logging.getLogger("iplotlogging-test-delete")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    return logger


def _touch(path: Path, days_old: float) -> None:
    """Create ``path`` and shift its mtime ``days_old`` days into the past."""
    path.write_text("x")
    past = time.time() - days_old * 86400
    os.utime(path, (past, past))


class DeleteOlderFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="iplotlogging_delete_"))
        self.logger = _silent_logger()

    def test_missing_path_is_noop(self):
        """Helpers must not crash if the log dir hasn't been created yet."""
        missing = self.tmp / "does_not_exist"
        delete_older_files(self.logger, str(missing), days=1)

    def test_keeps_five_most_recent_even_if_old(self):
        """The slice ``files[:-5]`` guarantees the five newest survive
        regardless of age — keeps a minimum trail for incident debugging."""
        for i in range(7):
            _touch(self.tmp / f"file_{i}.log", days_old=30)

        delete_older_files(self.logger, str(self.tmp), days=1)

        remaining = sorted(p.name for p in self.tmp.iterdir())
        self.assertEqual(len(remaining), 5)

    def test_removes_files_older_than_threshold(self):
        recent = self.tmp / "recent.log"
        old = self.tmp / "old.log"
        _touch(recent, days_old=0)
        _touch(old, days_old=20)
        # need extra padding so the floor of 5 doesn't keep `old`
        for i in range(5):
            _touch(self.tmp / f"padding_{i}.log", days_old=0)

        delete_older_files(self.logger, str(self.tmp), days=10)

        self.assertTrue(recent.exists(), "fresh file must survive")
        self.assertFalse(old.exists(),
                         "file older than threshold must be removed")

    def test_keeps_files_younger_than_threshold(self):
        for i in range(10):
            _touch(self.tmp / f"file_{i}.log", days_old=2)

        delete_older_files(self.logger, str(self.tmp), days=10)

        self.assertEqual(len(list(self.tmp.iterdir())), 10,
                         "no file is older than threshold; nothing removed")

    def test_permission_error_is_swallowed(self):
        """Real filesystems can deny removes; the helper must keep going
        rather than crash a long-running app."""
        for i in range(7):
            _touch(self.tmp / f"file_{i}.log", days_old=30)

        with unittest.mock.patch("os.remove",
                                 side_effect=PermissionError("denied")):
            # Must not raise.
            delete_older_files(self.logger, str(self.tmp), days=1)


class DeleteOlderLogsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="iplotlogging_logs_"))
        self.logger = _silent_logger()

    def test_targets_logs_subdirectory_of_iplot_log_path(self):
        logs_dir = self.tmp / "logs"
        logs_dir.mkdir()
        for i in range(7):
            _touch(logs_dir / f"old_{i}.log", days_old=30)

        # IPLOT_LOG_LIMIT is captured at module import (setupLogger.py:11),
        # so patching the env var has no effect — patch the module global directly.
        import iplotLogging.setupLogger as setup_logger
        with unittest.mock.patch.dict(
                "os.environ", {"IPLOT_LOG_PATH": str(self.tmp)}, clear=False), \
             unittest.mock.patch.object(setup_logger, "IPLOT_LOG_LIMIT", "1"):
            delete_older_logs(self.logger)

        self.assertEqual(len(list(logs_dir.iterdir())), 5,
                         "only the 5 newest must remain")


class DeleteOlderDumpsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="iplotlogging_dumps_"))
        self.logger = _silent_logger()

    def test_targets_dumps_subdirectory_of_iplot_dump_path(self):
        dumps_dir = self.tmp / "dumps"
        dumps_dir.mkdir()
        for i in range(7):
            _touch(dumps_dir / f"dump_{i}.scsv", days_old=30)

        import iplotLogging.setupLogger as setup_logger
        with unittest.mock.patch.dict(
                "os.environ", {"IPLOT_DUMP_PATH": str(self.tmp)}, clear=False), \
             unittest.mock.patch.object(setup_logger, "IPLOT_LOG_LIMIT", "1"):
            delete_older_dumps(self.logger)

        self.assertEqual(len(list(dumps_dir.iterdir())), 5)


if __name__ == "__main__":
    unittest.main()
