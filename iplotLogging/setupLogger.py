import logging
import os
import errno
import platform
import getpass
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

FILE_FORMATTER = logging.Formatter("[%(asctime)s.%(msecs)03d][%(hostname)s:%(username)s][%(processName)s:%(process)d][%(name)s-%(funcName)s][%(levelname)s]%(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')
CONSOLE_FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s.%(funcName)s:(%(filename)s:%(lineno)d) - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')


class HostnameFilter(logging.Filter):
    hostname = platform.node()

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True


class UserFilter(logging.Filter):
    username = getpass.getuser()

    def filter(self, record):
        record.username = UserFilter.username
        return True


def get_file_handler():
    userLoc = os.environ.get('PROTO_LOG_PATH')
    if userLoc is None:
        home = str(Path.home())
        dpath = home + "/.local/1Dtool/"
    else:
        dpath = userLoc
    userFile = os.environ.get('PROTO_LOG_FILENAME')
    if userFile is None:
        dfile = "protoplotQt5.log"
    else:
        dfile = userFile

    cusFolder = dpath + "/logs"
    # logging.config.fileConfig('logging.conf')
    # logging.basicConfig( format='%(asctime)s-%(levelname)s-%(process)d-%(funcName)s-%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    # filename="~/.local/1Dtool/logs/protoplotQt5.log",
    logger = logging.getLogger('root')
    try:
        os.makedirs(cusFolder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    filename = cusFolder + "/" + dfile
    file_handler = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=10, encoding='utf-8')
    file_handler.addFilter(HostnameFilter())
    file_handler.addFilter(UserFilter())
    file_handler.setFormatter(FILE_FORMATTER)
    return file_handler

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CONSOLE_FORMATTER)
    return console_handler

def formatLevel(lvl):
    if lvl == "INFO":
        return logging.INFO
    if lvl == "DEBUG":
        return logging.DEBUG
    if lvl == "WARNING":
        return logging.WARNING
    if lvl == "CRITICAL":
        return logging.CRITICAL
    if lvl == "ERROR":
        return logging.ERROR

    return logging.INFO


def get_logger(logger_name, level=None):
    logger = logging.getLogger(logger_name)
    if level:
        llevel = formatLevel(level)
    else:
        llevelX = os.environ.get('PROTO_LOG_LEVEL')
        if llevelX is None:
            llevel = logging.INFO
        else:
            llevel = formatLevel(llevelX)

    logger.setLevel(llevel)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_console_handler())
    return logger
