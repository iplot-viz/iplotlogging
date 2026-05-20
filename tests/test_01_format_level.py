"""Unit tests for ``format_level``.

The helper translates user-facing strings (read from env vars or passed
explicitly to ``get_logger``) to the integer constants exposed by the
stdlib ``logging`` module. A regression here would silently downgrade or
ignore the configured log level — easy to miss in production.
"""

import logging
import unittest

from iplotLogging.setupLogger import format_level


class FormatLevelTest(unittest.TestCase):
    def test_info_maps_to_logging_info(self):
        self.assertEqual(format_level("INFO"), logging.INFO)

    def test_debug_maps_to_logging_debug(self):
        self.assertEqual(format_level("DEBUG"), logging.DEBUG)

    def test_warning_maps_to_logging_warning(self):
        self.assertEqual(format_level("WARNING"), logging.WARNING)

    def test_error_maps_to_logging_error(self):
        self.assertEqual(format_level("ERROR"), logging.ERROR)

    def test_critical_maps_to_logging_critical(self):
        self.assertEqual(format_level("CRITICAL"), logging.CRITICAL)

    def test_unknown_level_falls_back_to_info(self):
        """Any input the function doesn't recognise must default to INFO,
        not raise — env-var typos shouldn't crash the app."""
        self.assertEqual(format_level("VERBOSE"), logging.INFO)
        self.assertEqual(format_level(""), logging.INFO)
        self.assertEqual(format_level(None), logging.INFO)


if __name__ == "__main__":
    unittest.main()
