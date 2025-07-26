import logging

def str_to_log_level (level: str):

    if 0 == level.find("DEBUG"):
        return logging.logging.DEBUG
    elif 0 == level.find("INFO"):
        return logging.logging.INFO
    elif 0 == level.find("WARNING"):
        return logging.logging.WARNING
    elif 0 == level.find("ERROR"):
        return logging.logging.ERROR
    elif 0 == level.find("CRITICAL"):
        return logging.logging.CRITICAL
    else:
        return logging.logging.ERROR
