"""Functions to handle
Usage instructions:
  Setup:
    In your main macro (in scintmc this is run.py), you must call setup_logger().
    Pass std=False to turn off printing to terminal.
    Pass a string to fname to make the
"""
import logging
import sys


LOG_NAME = 'velazquez_lab'


def setup_logger(lname=LOG_NAME, std=True, log=None, err=None):
  """Setup instance of logger with optional file and terminal I/O.
  Args:
    lname (str): name of logger
    std (bool): if True then logging info is printed to terminal
    log (str, None): log file name to write info to
    err (str, None): error file name to write errors to
  Returns:
    logger: instance of logger
  """
  print('...setting up logger')
  logger = logging.getLogger(lname)

  # Check if logger already initialized
  if logger.hasHandlers():
    logger.warn(f"Logger '{lname}' has already been setup. Nothing done.")
    return logger

  logger.setLevel(logging.DEBUG)

  # Setup IO handlers
  handlers = []
  if std:
    handlers.append(logging.StreamHandler(sys.stdout))
    handlers[-1].setLevel(logging.INFO)
  if log is not None:
    handlers.append(logging.FileHandler(filename=log, mode='w', encoding='utf-8'))
    handlers[-1].setLevel(logging.INFO)
  if err is not None:
    handlers.append(logging.FileHandler(filename=err, mode='w', encoding='utf-8'))
    handlers[-1].setLevel(logging.WARNING)

  # Setup formatting
  formatter = logging.Formatter('%(levelname)s (%(filename)s %(lineno)d): %(message)s')

  # Add handlers to logger
  for h in handlers:
    h.setFormatter(formatter)
    logger.addHandler(h)

  return get_logger(lname)


def get_logger(lname=LOG_NAME):
  """Return instance of logger.
  Args:
    lname (str): name of logger
  """
  return logging.getLogger(lname)



if __name__ == '__main__':
  """Demonstrate usage of logger.
  To run:
    python logger.py
  """

  logger = setup_logger(std=True, log='test.log', err='test.err')

  logger.debug('debug message')
  logger.info('info message')
  logger.warning('warn message')
  logger.error('error message')
  logger.critical('critical message')