import logging


def loggingConfig(testing):
    if testing:
        # * ``` Write to a new or existing log file! ``` * #
        # ! Testing! #
        # filemode='w' will not append to the file, it'll write over
        logging.basicConfig(
            filename="info.log",
            filemode="w",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
    else:
        # logging.basicConfig(filename='info.log',
        #                     level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        print(
            """
          Log file to be found at ./info.log!
      """
        )
        logging.info("master-blaster v1.1.0")
        logging.info("Creating a log file!!")