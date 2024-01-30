import logging
import os
import errno
import platform
import getpass
import sys
import datetime
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


def format_level(lvl):
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
    dpath = os.environ.get('PROTO_LOG_PATH') or f"{Path.home()}/.local/1Dtool"
    dfile = os.environ.get('PROTO_LOG_FILENAME') or f"mint_{platform.node()}_{os.getpid()}.log"

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


def get_logger(logger_name, level=None):
    logger = logging.getLogger(logger_name)
    if level:
        level2 = format_level(level)
    else:
        level2_x = os.environ.get('PROTO_LOG_LEVEL')
        if level2_x is None:
            level2 = logging.INFO
        else:
            level2 = format_level(level2_x)

    logger.setLevel(level2)
    logger.addHandler(FileHandlerIplot.fhandler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def delete_older_logs(logger):
    path = os.environ.get('PROTO_LOG_PATH') or f"{Path.home()}/.local/1Dtool"
    path += "/logs"
    days = os.environ.get('LIMIT_DAYS_LOGS_MINT') or 10
    actual_date = datetime.datetime.now()
    files = os.listdir(path)

    for file in files:
        full_path = os.path.join(path, file)

        if os.path.isfile(full_path):
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))

            days_diff = (actual_date - file_date).days

            if days_diff > days:
                try:
                    os.remove(full_path)
                    logger.info(f"Deleted file: {file}")
                except PermissionError:
                    logger.warning(f"Permission error deleting file: {file}")
                except Exception as e:
                    logger.warning(f"Failed while deleting file: {file} -> {e}")


class FileHandlerIplot(object):
    fhandler = get_file_handler()
