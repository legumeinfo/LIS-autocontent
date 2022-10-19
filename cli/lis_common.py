import os
import sys
import logging


def split_name(name):
    '''Split provided string into delimited parts, "." delimiter'''
    fields = name.split('.')  # split on delimiter
    return fields


def split_url(url):
    '''Splits URL into sub uri parts using "/"'''
    fields = url.split('/')  # split on delimiter
    return fields


def get_gensp(parts):
    '''Gets gensp and strain and from parts array and returns a tuple'''
    gensp = f'{parts[1].lower()[:3]}{parts[2][:2]}'  # make gensp from preparsed organismDir
    strain = parts[-2]  # get strain and key information
    return (gensp, strain)


def setup_logging(log_file, log_level, process):
    '''initializes a logger object with a common format'''
    log_level = getattr(logging, log_level.upper(), logging.INFO)  # set provided or set INFO
    msg_format = '%(asctime)s|%(name)s|[%(levelname)s]: %(message)s'
    logging.basicConfig(format=msg_format, datefmt='%m-%d %H:%M',
                        level=log_level)
    log_handler = logging.FileHandler(log_file, mode='w')
    formatter = logging.Formatter(msg_format)
    log_handler.setFormatter(formatter)
    logger = logging.getLogger(f"{process}")  # sets what will be printed for the log process
    logger.addHandler(log_handler)
    return logger
