# Copyright (c) 2020-2025 ITER Organization,
#               CS 90046
#               13067 St Paul Lez Durance Cedex
#               France
# Author IO
#
# This file is part of iplotlogging module.
# iplotlogging python module is free software: you can redistribute it and/or modify it under
# the terms of the MIT license.
#
# This file is part of ITER CODAC software.
# For the terms and conditions of redistribution or use of this software
# refer to the file LICENSE located in the top level directory
# of the distribution package
#


import logging
import os
import errno
import platform
import getpass
import sys
import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

IPLOT_LOG_LIMIT = os.environ.get('IPLOT_LOG_LIMIT')


class HostnameFilter(logging.Filter):
    hostname = platform.node()

    def filter(self, record) -> bool:
        record.hostname = HostnameFilter.hostname
        return True


class UserFilter(logging.Filter):
    username = getpass.getuser()

    def filter(self, record) -> bool:
        record.username = UserFilter.username
        return True


def format_level(lvl) -> int:
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


def get_file_handler() -> TimedRotatingFileHandler:
    dpath = os.environ.get('IPLOT_LOG_PATH') or f"{Path.home()}/.local/1Dtool"
    dfile = os.environ.get('IPLOT_LOG_FILENAME') or f"mint_{platform.node()}_{os.getpid()}.log"

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


def get_logger(logger_name, level=None) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    if level:
        level2 = format_level(level)
    else:
        level2_x = os.environ.get('IPLOT_LOG_LEVEL')
        if level2_x is None:
            level2 = logging.INFO
        else:
            level2 = format_level(level2_x)

    logger.setLevel(level2)
    logger.addHandler(FileHandlerIplot.fhandler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def delete_older_logs(logger):
    path = os.environ.get('IPLOT_LOG_PATH') or f"{Path.home()}/.local/1Dtool"
    path += "/logs"
    days = int(IPLOT_LOG_LIMIT) if IPLOT_LOG_LIMIT else 10

    delete_older_files(logger, path, days)


def delete_older_dumps(logger):
    path = os.environ.get('IPLOT_DUMP_PATH') or f"{Path.home()}/.local/1Dtool"
    path += "/dumps"
    days = int(IPLOT_LOG_LIMIT) if IPLOT_LOG_LIMIT else 10
    delete_older_files(logger, path, days)


def delete_older_files(logger, path, days):
    actual_date = datetime.datetime.now()
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    else:
        files = []

    files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)))

    for file in files[:-5]:
        full_path = os.path.join(path, file)

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
