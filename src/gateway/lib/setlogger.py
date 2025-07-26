from flask import logging

def str_to_log_level (level: str):

    if 0 == level.find("DEBUG"):
        return logging.DEBUG
    elif 0 == level.find("INFO"):
        return logging.INFO
    elif 0 == level.find("WARNING"):
        return logging.WARNING
    elif 0 == level.find("ERROR"):
        return logging.ERROR
    elif 0 == level.find("CRITICAL"):
        return logging.CRITICAL
    else:
        return logging.ERROR
