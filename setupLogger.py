import logging
import os
import errno
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def get_file_handler():
    userLoc = os.environ.get('PROTO_LOG_PATH')
    if userLoc is None:
        home = str(Path.home())
        dpath = home+"/.local/1Dtool/"
    else:
        dpath = userLoc
    userFile = os.environ.get('PROTO_LOG_FILENAME')
    if userFile is None:
        dfile = "protoplotQt5.log"
    else:
        dfile = userFile
    FORMATTER = logging.Formatter("%(asctime)s.%(msecs)03d-%(levelname)s-%(name)s-%(funcName)s-%(message)s", datefmt='%Y-%m-%dT%H:%M:%S')
    pid = os.getpid()
    cusFolder = dpath + "/p" + str(pid) + "/logs"
    #logging.config.fileConfig('logging.conf')
    #logging.basicConfig( format='%(asctime)s-%(levelname)s-%(process)d-%(funcName)s-%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    #filename="~/.local/1Dtool/logs/protoplotQt5.log",
    logger = logging.getLogger('root')
    try:
        os.makedirs(cusFolder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    filename = cusFolder + "/" + dfile
    file_handler = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=10,encoding='utf-8')
    file_handler.setFormatter(FORMATTER)
    return file_handler

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


def get_logger(logger_name,level=None):
    logger = logging.getLogger(logger_name)
    if level:
        llevel=formatLevel(level)
    else:
        llevelX = os.environ.get('PROTO_LOG_LEVEL')
        if llevelX is None:
            llevel=logging.INFO
        else:
            llevel = formatLevel(setLogLevel())

    logger.setLevel(llevel)
    logger.addHandler(get_file_handler())
    return logger





