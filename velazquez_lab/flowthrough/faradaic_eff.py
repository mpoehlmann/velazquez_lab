"""
Functions to calculate faradaic efficiency.
"""

import argparse
import pandas as pd


def calculate_faradaic_eff(area, avg_current, cal_slope, cal_intercept=0):
  """Faradaic efficiency calculator.
  Args:
    area (float, array_like): TODO (in mV/min/mA).
    avg_current (float): Average current (in mA).
    cal_slope (float, ufloat): GC calibration curve slope (in mV/min/mA).
    cal_intercept (float, ufloat): GC calibration curve intercept (in mV/min).
  Returns:
    fe (float, array_like): Faradaic efficiency (in percent).
  """
  current = (area-cal_intercept) / cal_slope
  fe = current / avg_current * 100
  return fe


def parse_args():
  """Parse commandline arguments for module."""
  ap = argparse.ArgumentParser()
  ap.add_argument('-a', '--area', type=float, required=True, help='Area in mV/.')
  ap.add_argument('-c', '--current', default=0, type=float, help='Average current in mA.')
  ap.add_argument('-e', '--currenterr', type=float, required=True, help='Error on average current in mA.')
  ap.add_argument('-f', '--file', type=str, required=True, help='Data file.')
  ap.add_argument('-p', '--plot', action='store_true', default=False, help='Plot fit.')
  args = vars(ap.parse_args())
  return args


if __name__ == '__main__':
  """Run module.
  To run:
    python velazquez_lab/flowthrough/faradaic_eff.py -f data/faradaic_eff.csv -a 0.0041 -c 10 -e 0.1
  """
  import matplotlib.pyplot as plt
  import uncertainties as un
  import velazquez_lab.utils.linear_fitting as ft

  # plt.style.use('jessica.mplstyle')
  args = parse_args()

  # Load input data files.
  df = pd.read_table(args['file'], header=(0), sep=',')
  colnames = {df.columns[i]: n for i, n in enumerate(('area', 'area_err', 'current', 'current_err'))}
  df.rename(columns=colnames, inplace=True)

  # Do calibration curve fitting.
  m_fit, b_fit, redchi = ft.chisq_linear_fit(df['current'], df['area'], err=df['current_err'], is_yerr=False)
  fig, ax = ft.plot_linear_fit(df['current'], df['area'], m_fit, b_fit, xerr=df['current_err'])
  ax.set(xlabel='Current (mA)', ylabel='Area (mV/s)')
  print(f"m = {m_fit}")
  print(f"b = {b_fit}")
  print(f"redchi = {redchi:.4g}")

  # Calculate faradaic efficiency
  fe = calculate_faradaic_eff(area=args['area'], avg_current=un.ufloat(args['current'], args['currenterr']), cal_slope=m_fit, cal_intercept=b_fit)
  print(f"Faradaic efficiency: {fe}%")

  if args['plot']:
    plt.show()