#!/usr/bin/env python3
"""Create polarization curves."""

import os

from velazquez_lab.utils import logger
from velazquez_lab.pol.ecsa import ECSA


def create_pol_curves(folder, config):
  """Create polarization curves.
  Args:
    folder (str): folder to recursively run on
    config (dict): configuration parameters
  """
  log = logger.get_logger(folder)

  # Calculate electrochemical surface area
  ecsa = ECSA(folder, config)
  ecsa_val, ecsa_data = ecsa.process()

  log.info('Great success!')


if __name__ == '__main__':
  """Create polarization curves.
  To run:
    cd scripts
    python create_pol_curves.py
  Info:
    In each folder containing data, add a configuration file called 'metadata.txt'.
    This should resemble the following format:

    Each ECSA data file must:
      1) end in '.txt'
      2) contain '_CV_' or '_cv_'
      3) contain '_SCANRATE_' for the rates listed in the configuration file

    Each polarization data file must:
      1) end in '.txt'
      2) contain '_LSV_' or '_lsv'
  """
  import velazquez_lab.utils.config_parser as cp

  # Inputs
  data_folder = '../'
  config_fname = 'metadata.txt'

  # Loop recursively over files and folders in folder
  for path, dirs, files in os.walk(data_folder):
    if config_fname in files:  # Only run on folders containing configuration file
      # Setup logging
      log = logger.setup_logger(lname=path, log=f"{path}/pol_log.out", err=f"{path}/pol_log.err")
      log.info(f"Data folder: {path}")

      # Parse configuration
      config = cp.parse_config(f"{path}/{config_fname}")

      # Create polarization curves
      create_pol_curves(path, config)