"""
Calculate specific capacitance.
"""

import argparse
import numpy as np
import pandas as pd
from shapely.geometry import Polygon

def calculate_specific_cap(potentials, currents, scan_rates, mass=None, surf_area=None):
  """Calculates specific capacitance in units of F/g or F/cm2 depending on the input normalization.
  Args:
    potentials (array_like): potentials (in V) for each scan
    currents (array_like): currents (in mA) for each scan
    scan_rates (array_like): scan rate (in mV/s for each scan)
    mass (float): mass (in g) of catalyst
    surf_area (float): surface area (in cm2) of electrode
  Returns:
    float: mass-normalized specific capacitance (in F/g)
    float: area-normalized specific capacitance (in F/cm2)
    pd.DataFrame: calculations
  """
  rows = []
  for e, i, r in zip(potentials, currents, scan_rates):
    _i = np.asarray(i) / 1000  # Convert mA to A
    _r = r / 1000  # Convert mV/s to V/s
    delta_v = max(e) - min(e)
    pgon = Polygon(zip(e, _i))
    _row = [r, pgon.area, 0.5*pgon.area/(_r*delta_v)]  # Area units: Amps*Volts=C
    _row.append(_row[2]/mass if mass is not None else None)
    _row.append(_row[2]/surf_area if surf_area is not None else None)
    rows.append(_row)
  df = pd.DataFrame(rows, columns=['scan_rate', 'area', 'csp', 'csp_g', 'csp_cm2'])
  avg_csp_g = df['csp_g'].mean() if mass is not None else None
  avg_csp_cm2 = df['csp_cm2'].mean() if surf_area is not None else None
  return avg_csp_g, avg_csp_cm2, df


def parse_args():
  ap = argparse.ArgumentParser()
  ap.add_argument('-a', '--area', default=None, type=float, help='Surface area (in cm2) of electrode')
  ap.add_argument('-c', '--cycle', default=None, type=int, help='Cycle number')
  ap.add_argument('-f', '--files', nargs='+', required=True, help='Data files')
  ap.add_argument('-m', '--mass', default=None, type=float, help='Mass (in g) of catalyst')
  ap.add_argument('-s', '--scanrates', nargs='+', type=int, required=True, help='Scan rates (in mV/s)')
  args = vars(ap.parse_args())
  return args



if __name__ == "__main__":
  """
  Examples:
    data/cv_doublelayer:
      python ecsa.py -f 2-6-2021_K2Mo6S6_sample1_her_03_CV_C02.txt 2-6-2021_K2Mo6S6_sample1_her_04_CV_C02.txt 2-6-2021_K2Mo6S6_sample1_her_05_CV_C02.txt 2-6-2021_K2Mo6S6_sample1_her_06_CV_C02.txt 2-6-2021_K2Mo6S6_sample1_her_07_CV_C02.txt -s 5 20 50 100 200 --cycle 2 -m 0.000117 -a 0.504
  """
  import matplotlib.pyplot as plt
  from velazquez_lab.pol.ecsa import load_data

  args = parse_args()

  """Load input data files."""
  potentials, currents = load_data(args['files'], cycle=args['cycle'])

  """Calculate specific capacitance (c_sp)."""
  csp_g, csp_cm2, df = calculate_specific_cap(potentials, currents, scan_rates=args['scanrates'], mass=args['mass'], surf_area=args['area'])
  print(f"Mass-normalized specific capacitance = {csp_g:.4e} F/g")
  print(f"Area-normalized specific capacitance = {csp_cm2:.4e} F/cm2")
  print(df)

  """Make plots."""
  fig, axes = plt.subplots(figsize=(12,3), ncols=3, constrained_layout=True)
  ax = axes[0]
  ax.set(xlabel='Potential (V)', ylabel='Current (mA)')
  for e, i, s in zip(potentials, currents, args['scanrates']):
    ax.plot(e, i, label=s)
  ax.legend(title='Scan rate (mV/s)')

  ax = axes[1]
  ax.set(xlabel='Scan rate (mV/s)', ylabel='Specific capacitance (F/g)')
  ax.plot(df['scan_rate'], df['csp_g'], 'o')

  ax = axes[2]
  ax.set(xlabel='Scan rate (mV/s)', ylabel='Specific capacitance (F/cm$^{2}$)')
  ax.plot(df['scan_rate'], df['csp_cm2'], 'o')

  plt.show()