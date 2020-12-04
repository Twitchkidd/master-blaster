import logging

# logging #
# * Handle logging operations and errors to the log file. * #


def loggingConfig(testing):
    """Configure logging. Report logfile location."""
    # * ``` If testing, write to new or overwrite existing log file! ``` * #
    if testing:
        # filemode='w' will not append to the file, it'll write over
        logging.basicConfig(
            filename="info.log",
            filemode="w",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
    else:
        logging.basicConfig(
            filename="info.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
    print(
        """
        Log file to be found at ./info.log!
    """
    )
    logging.info("master-blaster v1.1.0")
    logging.info("Creating a log file!!")


def logInfo(info):
    """Invoke the logger at the INFO level."""
    logging.info(info)


def logWarning(warning):
    """Invoke the logger at the WARNING level."""
    logging.warning(warning)


def logCrash(error):
    """AAAAHHHHH!!!!"""
    logging.error(error)