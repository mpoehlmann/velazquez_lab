"""Functions for linear fitting.
Also see notebooks/linear_fitting.ipynb.
"""

import lmfit
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import uncertainties as un
from uncertainties import unumpy

from velazquez_lab.utils import styles


def linear_eqn(x, m, b):
  """Equation for a line."""
  return m*x + b

def chisq_linear(m, b, x, y, x_err=None, y_err=None):
  """Chi-squared values (sum of squared residuals) for data with errors fit to a linear model."""
  y_pred = linear_eqn(x, m=m, b=b)
  if x_err is None and y_err is None:
    return (y - y_pred)**2
  elif x_err is None:
    return (y - y_pred)**2 / y_err**2
  else:
    return (y - y_pred)**2 / (m**2*x_err**2 + y_err**2)

def linear_fit(x, y, x_err=None, y_err=None, m_init=1, b_init=0, m_range=(-np.inf, np.inf), b_range=(-np.inf, np.inf), vary_m=True, vary_b=True, is_verbose=False, return_fitres=False):
  """Perform a linear fit using a chi squared fit.
  Args:
    x (array_like): X data values.
    y (array_like): Y data values.
    x_err (array_like, None): X data errors. If None then X errors are not included in the fit.
    y_err (array_like, None): Y data errors. If None then Y errors are not included in the fit.
    m_init (float): Initial value for slope.
    b_init (float): Initial value for intercept.
    m_range (tuple): Range for slope.
    b_range (tuple): Range for intercept.
    vary_m (bool): Whether to vary the slope. If False then the value is fixed to m_init.
    vary_b (bool): Whether to vary the intercept. If False then the value is fixed to b_init.
    is_verbose (bool): Whether to print the fit details.
    return_fitres (bool): Whether to return the fit results.
  Returns:
    m_fit (un.ufloat): Best-fit slope with uncertainty.
    b_fit (un.ufloat): Best-fit intercept with uncertainty.
    redchi (float): Reduced chi-squared value.
  Notes:
    Errors on X and Y: https://aip.scitation.org/doi/pdf/10.1063/1.4823074
  """
  # Setup parameters.
  params = lmfit.Parameters()
  params.add('m', value=m_init, min=m_range[0], max=m_range[1], vary=vary_m)
  params.add('b', value=b_init, min=b_range[0], max=b_range[1], vary=vary_b)

  # Do fit.
  _chisq_linear = lambda params: chisq_linear(params['m'], params['b'], x, y, x_err, y_err)
  result = lmfit.minimize(_chisq_linear, params)
  if is_verbose:
    # print(f"Is fit valid = {result.status()}")
    print(lmfit.fit_report(result))
  m_fit = un.ufloat(result.params['m'].value, result.params['m'].stderr)
  b_fit = un.ufloat(result.params['b'].value, result.params['b'].stderr)
  if return_fitres:
    return m_fit, b_fit, result.redchi, result
  return m_fit, b_fit, result.redchi

def plot_linear_fit(x, y, m, b, x_err=None, y_err=None, redchi=None):
  """Plot the linear fit with error pars."""
  if x_err is None:
    x_err = np.zeros(x.size)
  if y_err is None:
    y_err = np.zeros(y.size)

  # Setup figure.
  fig, ax = plt.subplots(constrained_layout=True)
  ax.set(xlabel='x', ylabel='y')
  ax.errorbar(x, y, xerr=x_err, yerr=y_err, markersize=4, fmt='o', color=styles.COLORS[0], zorder=3)
  # ax.plot(x, y, 'o', markersize=4, color=styles.COLORS[0], zorder=3)
  # for _x, _y, _x_err, _y_err in zip(x, y, x_err, y_err):
  #   ellipse = mpl.patches.Ellipse(xy=(_x, _y), width=2*_x_err, height=2*_y_err, edgecolor=styles.color_to_rgba(styles.COLORS[0], 1, lib='mpl'), fc=styles.color_to_rgba(styles.COLORS[0], 0.3, lib='mpl'), lw=0.75)
  #   ax.add_patch(ellipse)

  # Add fitted line and error band.
  x_fit = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 101)
  y_fit = linear_eqn(unumpy.uarray(x_fit, np.zeros(x_fit.size)), m, b)
  ax.plot(x_fit, unumpy.nominal_values(y_fit), color=styles.COLORS[1], zorder=2)
  ax.fill_between(x_fit, unumpy.nominal_values(y_fit)-unumpy.std_devs(y_fit), unumpy.nominal_values(y_fit)+unumpy.std_devs(y_fit), fc=styles.COLORS[1], ec=None, alpha=0.4, zorder=1)
  # ax.fill_between(x_fit, unumpy.nominal_values(y_fit)-2*unumpy.std_devs(y_fit), unumpy.nominal_values(y_fit)+2*unumpy.std_devs(y_fit), fc=styles.COLORS[1], ec=None, alpha=0.1, zorder=1)
  ax.set_xlim(x_fit[0], x_fit[-1])

  # Add equation.
  txt = rf"y = $({m:L}) x$  +  $({b:L})$"
  txt += "\n"
  if redchi is not None:
    txt += rf"$\chi^{{2}}_{{red}}$ = {redchi:.4g}"
  ax.text(0.1, 0.9, txt, fontsize='small', ha='left', va='top', transform=ax.transAxes)
  return fig, ax

def plot_chi(x, y, m, b, x_err=None, y_err=None):
  """Plot chi values for each data point."""
  # Sort data to ascending x.
  df = pd.DataFrame().from_dict({
    'x': x,
    'y': y,
    'x_err': x_err if x_err is not None else np.zeros(x.size),
    'y_err': y_err if y_err is not None else np.zeros(y.size),
  })
  df.sort_values('x', inplace=True)

  # Calculate chi values.
  _m, _b = (m.n, b.n) if isinstance(m, un.UFloat) else (m, b)
  chi = df['y'] - linear_eqn(df['x'], _m, _b)
  if x_err is not None and y_err is not None:
    wt_sq = _m**2*x_err**2 + y_err**2
  elif x_err is not None:
    wt_sq = _m**2 * x_err**2
  elif y_err is not None:
    wt_sq = y_err**2
  else:
    wt_sq = np.ones(x.size)
  chi /= np.sqrt(wt_sq)

  # Make the figure.
  fig, ax = plt.subplots()
  ax.bar(np.arange(x.size), chi)
  ax.set(xlabel='Data point', ylabel='$\chi$')
  return fig, ax


if __name__ == '__main__':
  import pandas as pd

  # Load data file.
  df = pd.read_table('../../data/linear_fit_xyerr.csv', header=0, sep=',')

  # Do fit.
  m_fit, b_fit, redchi = linear_fit(df['x'], df['y'], x_err=df['x_err'], y_err=df['y_err'], is_verbose=True)
  print(f"m = {m_fit}")
  print(f"b = {b_fit}")
  print(f"redchi = {redchi:.4g}")

  # Draw plot.
  styles.set_matplotlib_style()
  fig, ax = plot_linear_fit(df['x'], df['y'], m_fit, b_fit, x_err=df['x_err'], y_err=df['y_err'], redchi=redchi)
  fig, ax = plot_chi(df['x'], df['y'], m_fit, b_fit, x_err=df['x_err'], y_err=df['y_err'])
  plt.show()