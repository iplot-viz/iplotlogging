"""Unit tests for ``HostnameFilter`` and ``UserFilter``.

These filters decorate every log record with hostname and username,
which is what makes IDV logs traceable across the cluster. A silent
break (filter returning False, missing attribute) drops records on the
floor or strips identifying info that on-call relies on to debug.
"""

import logging
import unittest

from iplotLogging.setupLogger import HostnameFilter, UserFilter


def _make_record() -> logging.LogRecord:
    return logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__,
        lineno=1, msg="hello", args=(), exc_info=None)


class HostnameFilterTest(unittest.TestCase):
    def test_filter_attaches_hostname_to_record(self):
        record = _make_record()
        self.assertFalse(hasattr(record, "hostname"))

        kept = HostnameFilter().filter(record)

        self.assertTrue(kept, "filter must keep the record")
        self.assertEqual(record.hostname, HostnameFilter.hostname)

    def test_hostname_class_attribute_is_non_empty(self):
        """``platform.node()`` returns a string even on minimal systems."""
        self.assertIsInstance(HostnameFilter.hostname, str)


class UserFilterTest(unittest.TestCase):
    def test_filter_attaches_username_to_record(self):
        record = _make_record()
        self.assertFalse(hasattr(record, "username"))

        kept = UserFilter().filter(record)

        self.assertTrue(kept)
        self.assertEqual(record.username, UserFilter.username)

    def test_username_class_attribute_is_non_empty(self):
        self.assertIsInstance(UserFilter.username, str)
        self.assertTrue(UserFilter.username)


if __name__ == "__main__":
    unittest.main()
