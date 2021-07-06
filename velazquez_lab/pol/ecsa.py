"""Electrochemical surface area calculator.

Info:
  The data file's first column contains potential (in V).
  The second column contains the current (in mA).
  The third column (optionally) contains the cycle index.
"""

from dash_bootstrap_components._components.Label import Label
import numpy as np
import pandas as pd

from velazquez_lab.utils import fitting


def load_data(files, cycle=None, header=(0), **kwargs):
  """Loads data file contents into lists of potentials and currents.
  Args:
    files (str, array_like): Data files to load.
    cycle (int, None): Cycle index (3rd column in data file) to select.
      All data in the file is used if this is None.
    header (array_like, None): Header lines, passed to pd.read_table.
    **kwargs: Passed to pd.read_table
  Returns:
    array_like: potentials
    array_like: currents
  """
  potentials, currents = list(), list()
  for f in np.atleast_1d(files):
    df = pd.read_table(f, header=header, **kwargs)
    if cycle is not None:  # Select data for a given cycle (3rd column)
      df = (df[df.iloc[:, 2]==cycle])
    potentials.append(df.iloc[:, 0])
    currents.append(df.iloc[:, 1])
  return potentials, currents


def calculate_ecsa(potentials, currents, scan_rates, contour, specific_cap=1, blank_cap=0):
  """Calculates electrochemical surface area in units of FIXME.
  Args:
    potentials (array_like): potentials (in V) for each scan
    currents (array_like): currents (in mA) for each scan
    scan_rates (array_like): scan rate (in mV/s for each scan)
    contour (float): potential
    specific_cap (float): specific capacitance (in F/cm^2)
    blank_cap (float): blank capacitance (in F)
  Returns:
    float: electrochemical surface area
    pd.DataFrame:
  TODO:
    Generalize this implementation.
    Fix blank capacitance
  """
  """Prepare data."""
  rows = []
  for row, (e, i, r) in enumerate(zip(potentials, currents, scan_rates)):
    mid_idx = np.argmin(e)  # Find minimum potential to divide data in half
    i1, i2 = ( np.interp(contour, e[idx], i[idx]) for idx in (slice(0,mid_idx),slice(mid_idx,None)) )  # Interpolate on line for each half
    rows.append([r, min(i1, i2), max(i1, i2)])
  df = pd.DataFrame(rows, columns=['scan rate', 'I low', 'I high'])

  """Fit contours."""
  for i, key in enumerate(('low', 'high')):
    fitres, vals = fitting.linear_fit(df['scan rate'], df[f'I {key}'])
    df.insert(len(df.columns), f'slope {key}', pd.Series(vals['m']))
    df.insert(len(df.columns), f'intercept {key}', pd.Series(vals['b']))
    df.insert(len(df.columns), f'rsq {key}', pd.Series(1-fitres.residual.var()/np.var(df[f'I {key}'])))

  avg_slope = 0.5 * (np.abs(df.loc[0, 'slope low'])+np.abs(df.loc[0, 'slope high']))  # Units are mA*s/mV=F
  ecsa_val = (avg_slope-blank_cap) / specific_cap
  return ecsa_val, df



if __name__ == '__main__':
  """Example Tafel slope analysis.
  Examples:
    python ecsa.py -f 1-12-2021_K2Mo6Te8_sample1_her_03_CV_C03.txt 1-12-2021_K2Mo6Te8_sample1_her_04_CV_C03.txt 1-12-2021_K2Mo6Te8_sample1_her_05_CV_C03.txt 1-12-2021_K2Mo6Te8_sample1_her_06_CV_C03.txt 1-12-2021_K2Mo6Te8_sample1_her_07_CV_C03.txt -s 3 4 5 6 7 --cycle 2
  """
  import argparse
  import matplotlib.pyplot as plt
  # plt.style.use('jessica.mplstyle')

  ap = argparse.ArgumentParser()
  ap.add_argument('--blank', default=0, type=float, help='Blank capacitance in F')
  ap.add_argument('-c', '--cycle', default=None, type=int, help='Cycle number')
  ap.add_argument('-f', '--files', nargs='+', required=True, help='Data files')
  ap.add_argument('-p', '--potential', required=True, type=float, help='Potential (in V) at which ECSA is calculated')
  ap.add_argument('-s', '--scanrates', nargs='+', type=int, required=True, help='Scan rates (in mV/s)')
  ap.add_argument('--specific', default=1, type=float, help='Specific capacitance (in F/cm^2)')
  args = vars(ap.parse_args())

  """Load input data files."""
  potentials, currents = load_data(args['files'], cycle=args['cycle'])

  """Calculate ECSA."""
  ecsa_val, df = calculate_ecsa(potentials, currents, scan_rates=args['scanrates'], contour=args['potential'], specific_cap=args['specific'], blank_cap=args['blank'])

  """Make plots."""
  fig, axes = plt.subplots(figsize=(10,4), ncols=2, constrained_layout=True)
  ax = axes[0]
  ax.set(xlabel='Potential (V)', ylabel='Current (mA)')
  for e, i, s in zip(potentials, currents, args['scanrates']):
    ax.plot(e, i, label=s)
  ax.axvline(args['potential'], label='Potential contour', color='lightgray', linestyle='--')
  ax.legend(title='Scan rate (mV/s)')

  ax = axes[1]
  ax.set(title=f"Potential = {args['potential']} V", xlabel='Scan rate (mV/s)', ylabel='Current (mA)')
  for key, color in (('low', 'tab:blue'), ('high', 'tab:orange')):
    ax.plot(df['scan rate'], df[f'I {key}'], 'o', color=color, label=f'I {key} (mA)')
    y = df['scan rate']*df.loc[0, f'slope {key}'] + df.loc[0, f'intercept {key}']
    ax.plot(df['scan rate'], y, '-', color=color, label=f'I {key} (mA)')

  plt.show()