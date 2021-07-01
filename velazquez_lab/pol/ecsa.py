"""Electrochemical surface area calculator."""

import numpy as np
import pandas as pd

from velazquez_lab.utils import fitting


def load_data(files, scan_rates, cycle=2, header=(0), **kwargs):
  """Loads data file contentss into a dictionary of pd.DataFrames.
  The data file's first column contains potential in volts.
  The second column contains the current in mA.
  The third column (optionally) contains the cycle index.

  Args:
    files (str, array_like): Data files to load.
    scan_rates (int, array_like): Scan rate in UNITS for the corresponding data file.
    cycle (int, None): Cycle index (3rd column in data file) to select.
      All data in the file is used if this is None.
    header (array_like, None): Header lines, passed to pd.read_table.
    **kwargs: Passed to pd.read_table

  Returns:
    dict: dictionary of DataFrames with data file content.
      The dictionary key is the scan rate.
  """
  dfs = dict()
  for file, rate in zip(np.atleast_1d(files), np.atleast_1d(scan_rates)):
    df = pd.read_table(file, header=header, **kwargs)
    if cycle is not None:
      df = (df[df.iloc[:,2]==cycle])
    dfs[rate] = df
  return dfs


def fit_potential_contour(dfs, contour):  # TODO: clean up
  # Prepare data
  rates, currents_low, currents_high = ([] for _ in range(3))
  for rate, df in dfs.items():
    mid_idx = np.argmin(df.iloc[:,0])  # Find minimum potential to divide data in half
    i1, i2 = ( np.interp(contour, df.iloc[idx,0], df.iloc[idx,1]) for idx in (slice(0,mid_idx),slice(mid_idx,None)) )  # Interpolate on line for each half
    rates.append(rate)
    currents_low.append(min(i1, i2))
    currents_high.append(max(i1, i2))
  out_df = pd.DataFrame.from_dict({0: rates, 1: currents_low, 2:currents_high})

  # Do fitting
  fitres = dict()
  fitresult_low, optvals_low = fitting.linear_fit(rates, currents_low)
  fitres['m_low'], fitres['b_low'] = optvals_low['m'], optvals_low['b']
  fitres['rsq_low'] = 1 - fitresult_low.residual.var() / np.var(currents_low)

  fitresult_high, optvals_high = fitting.linear_fit(rates, currents_high)
  fitres['m_high'], fitres['b_high'] = optvals_high['m'], optvals_high['b']
  fitres['rsq_high'] = 1 - fitresult_high.residual.var() / np.var(currents_high)

  fitres['m_avg'] = 0.5 * (abs(fitres['m_low'])+abs(fitres['m_high']))

  # print(f"\nLower slope: {fitres['m_low']}")
  # print(f"  r squared = {fitres['rsq_low']}")
  # print(f"Higher slope: {fitres['m_high']}")
  # print(f"  r squared = {fitres['rsq_high']}")
  # print(f"Average slope: {fitres['m_avg']}")
  return out_df, fitres


def calculate_ecsa(dfs, contour, specific_capacitance=1, blank_capacitance=0):
  """Electrochemical surface area calculator.
  Args:
    files (list): list of data file names
  """
  out_df, fitres = fit_potential_contour(dfs, contour)
  val = (fitres['m_avg']-blank_capacitance) / specific_capacitance
  return val, out_df, fitres