import logging
import os
import errno
import platform
import getpass
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


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


def get_file_handler():
    user_loc = os.environ.get('PROTO_LOG_PATH')
    if user_loc is None:
        home = str(Path.home())
        dpath = home + "/.local/1Dtool/"
    else:
        dpath = user_loc
    user_file = os.environ.get('PROTO_LOG_FILENAME')
    if user_file is None:
        dfile = f"mint_{platform.node()}_{os.getpid()}.log"
    else:
        dfile = user_file
    formatter = logging.Formatter("[%(asctime)s.%(msecs)03d][%(hostname)s:%(username)s][%(processName)s:%(process)d]"
                                  "[%(name)s-%(funcName)s][%(levelname)s]%(message)s", datefmt='%Y-%m-%dT%H:%M:%S')

    cus_folder = dpath + "/logs"
    # logging.config.fileConfig('logging.conf')
    # logging.basicConfig( format='%(asctime)s-%(levelname)s-%(process)d-%(funcName)s-%(message)s',
    #                      datefmt='%Y-%m-%dT%H:%M:%S')
    # filename="~/.local/1Dtool/logs/protoplotQt5.log",
    # logger = logging.getLogger('root')
    try:
        os.makedirs(cus_folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    filename = cus_folder + "/" + dfile
    file_handler = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=10, encoding='utf-8')
    file_handler.addFilter(HostnameFilter())
    file_handler.addFilter(UserFilter())
    file_handler.setFormatter(formatter)
    return file_handler


class FileHandlerIplot(object):
    fhandler = get_file_handler()


def get_logger(logger_name, level=None):
    logger = logging.getLogger(logger_name)
    if level:
        llevel = formatLevel(level)
    else:
        llevel_x = os.environ.get('PROTO_LOG_LEVEL')
        if llevel_x is None:
            llevel = logging.INFO
        else:
            llevel = formatLevel(llevel_x)

    logger.setLevel(llevel)
    logger.addHandler(FileHandlerIplot.fhandler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger
