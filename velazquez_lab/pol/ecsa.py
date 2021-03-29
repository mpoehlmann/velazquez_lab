"""Calculate electrochemical surface area."""

# scan_rates
# cs
# potential_contour
# blank_capacitance

import matplotlib.pyplot as plt
import numericalunits as nu
import numpy as np
import os
import pandas as pd

from velazquez_lab.utils import logger
from velazquez_lab.utils import files


class ECSA:
  """Electrochemical surface area calculator.
  Notes:
    Each ECSA data file must:
      1) end in '.txt'
      2) contain '_CV_' or '_cv_'
      3) contain '_SCANRATE_' for the rates listed in the configuration file
    Data file format:
      1st column: potential (Ewe) in V
      2nd column: current (<I>) in mA
      3rd column: cycle number
      1st row: column labels (this is ignored by the code)
  """

  def __init__(self, path, config):
    """Constructor.
    Args:
      config (dict): configuration parameters
        steps: list
        scan_rates: list
        cycle: int
    """
    self.config = config['ecsa']  # Get configuration

  def process(self):
    """Calculate electrochemical surface area.
    Args:
      path (str): path to data folder with CV files
    """
    self.path = path
    self.log = logger.get_logger(self.path)  # Setup logging
    self._load_data()

    potential_contour = self.config.get('potential_contour')
    good_steps = list(self.dfs.keys())
    while True:  # Use while loop for user input
      # TODO: draw plot

      # User input for potential
      if potential_contour is None:
        potential_contour = input('\nWhich potential do you want (in V)? ')

      # Get potential contour values to plot
      rates, current_low, current_high = (dict() for _ in range(3))  # Reset v
      for step, df in self.dfs.items():
        if step not in good_steps:  # Skip unwanted steps
          continue
        mid_idx = np.argmin(df.iloc[:,0])  # Find minimum potential to divide data in half
        i1, i2 = ( np.interp(potential_contour, df.iloc[idx,0], df.iloc[idx,1]) for idx in (slice(0,mid_idx),slice(mid_idx,None)) )  # Interpolate on line for each half
        current_low[step] = min(i1, i2)
        current_high[step] = max(i1, i2)
        rates[step] = self.config['scan_rates'][step]

      # TODO: draw plot and do fits

      # Check if done
      is_done = input('\nIs this good (y or n)? ')
      if is_done.lower()=='y':
        plt.close('all')
        break

      # Choose action
      print('Do you want to:')
      print('  1. Keep this potential and throw away some points')
      print('  2. Choose a different potential')
      while True:  # Use while loop for user input
        action = int(input())
        if action == 1:
          pts = input(f'Which points would you like to discard (1-{len(good_steps)} from left to right)? ')
          for p in np.array(list(map(int,pts.strip().split())))-1:
            good_steps.remove(p)  # Minus 1 to get index
            self.log.info(f'Discarding point: {good_steps[p]}')
          break
        elif action == 2:
          potential_contour = None
          break
        else:
          print('Not a valid option. Try again.')

    return x/cs, output  # Divide by specific capacitance, divide by 1000000 to convert units


  # def draw(self):
  #   """Draw ECSA plots."""
  #   # TODO

  #   # Setup ECSA plots
  #   self.colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
  #   self.fig1, self.ax1 = plt.subplots(figsize=(6,4), constrained_layout=True)
  #   self.ax1.set(xlabel='Potential (V)', ylabel='Current (mA)')
  #   self.fig2, self.ax2 = plt.subplots(figsize=(6,4), constrained_layout=True)


  # def save(self, fname):
  #   """Save ECSA data to file.
  #   Args:
  #     fname (str): output file name
  #   """
  #   ecsa_df = pd.DataFrame.from_dict(ecsa_data, orient='index')
  #   ecsa_df = ecsa_df.transpose()
  #   ecsa_df.to_csv(output_ecsa_fname, index=False)
  #   self.log.info(f"Saving {fname}")


  def _load_data(self):
    """Load ECSA data (CV files)."""
    self.dfs = dict()
    for step, scan_rate in self.config['scan_rates'].items():
      # Find file name for step
      fname = files.get_files(self.path, rf'(.*_{step}_+.*(cv|CV).*|.*_(cv|CV).*_+{step}_+.*)', 'txt', 1)
      self.log.info(f"ECSA file:\n  {fname}")

      # Load data from text files
      df = pd.read_csv(f"{self.path}/{fname}", usecols=(0,1,2), sep='\t', header=(0))

      # Select values for specified cycle
      self.dfs[step] = df[df.iloc[:,2]==self.config['cycle']]