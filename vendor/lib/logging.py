import logging


def logging_config(testing):
    """Set write over instead of append to file if testing,
    and report logfile location."""
    if testing:
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
    logging.info("master-blaster v1.1.0")
    logging.info("Creating a log file!!")