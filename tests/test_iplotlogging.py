"""
Test get_logger function
"""
from iplotLogging.setupLogger import get_logger


def test_function_get_logger():
    test_logger_object = get_logger("TestLogger")
    assert test_logger_object is not None, "Could not create logger object"
    test_logger_object.debug("Bug found")
