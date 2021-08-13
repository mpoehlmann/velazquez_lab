"""
Functions for linear fitting.
"""

import lmfit
import matplotlib.pyplot as plt
import numpy as np
import uncertainties as un
from uncertainties import unumpy


def linear_eqn(x, m, b):
  """Equation for a line."""
  return m*x + b

def linear_fit(x, y):
  """Fit data to linear model."""
  myfit = lmfit.Model(linear_eqn)
  pars = myfit.make_params()
  pars['m'].set(value=0, vary=True)
  pars['b'].set(value=0, vary=True)

  fitresult = myfit.fit(y, pars, x=x)
  optvals = fitresult.best_values

  return fitresult, optvals


def linear_residuals(params, x, y, y_err=None):
  """Residuals for a linear function."""
  y_pred = linear_eqn(x, params['m'], params['b'])
  return (y-y_pred)**2 if y_err is None else (y-y_pred)**2/y_err**2


def chisq_linear_fit(x, y, err=None, is_yerr=True, m_init=1, b_init=0, m_range=(-np.inf, np.inf), b_range=(-np.inf, np.inf), vary_m=True, vary_b=True, is_verbose=False):
  """Perform a linear fit using a chi squared fit.
  Args:
    x (np.ndarray(float)): x values
    y (np.ndarray(float)): y values
    err (np.ndarray(float)): error values
    is_yerr (bool): if True then err is the error on y values, if False then err is the error on x values
  """
  xv, yv, ye = (x, y, err) if is_yerr else (y, x, err)

  # Setup parameters.
  params = lmfit.Parameters()
  params.add('m', value=m_init, min=m_range[0], max=m_range[1], vary=vary_m)
  params.add('b', value=b_init, min=b_range[0], max=b_range[1], vary=vary_b)

  # Do fit.
  result = lmfit.minimize(linear_residuals, params, args=(xv, yv, ye))
  if is_verbose:
    # print(f"Is fit valid = {result.status()}")
    print(lmfit.fit_report(result))
  m_fit = un.ufloat(result.params['m'].value, result.params['m'].stderr)
  b_fit = un.ufloat(result.params['b'].value, result.params['b'].stderr)

  if not is_yerr:  # Invert if input error is on x.
    b_fit, m_fit = -b_fit/m_fit, 1/m_fit
  return m_fit, b_fit, result.redchi


def plot_linear_fit(x, y, m, b, xerr=None, yerr=None, redchi=None):
  """Plot linear fit.
  Args:
    TODO
  """
  if xerr is None:
    xerr = np.zeros(x.shape)
  if yerr is None:
    yerr = np.zeros(x.shape)

  # Setup figure.
  colors = ['#9D7FC1', '#5589BA']
  fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
  ax.set(xlabel='x', ylabel='y')
  ax.errorbar(x, y, xerr=xerr, yerr=yerr, markersize=4, fmt='o', color=colors[0], zorder=3)

  # Add fitted line and error band.
  x_fit = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 100)
  y_fit = linear_eqn(unumpy.uarray(x_fit, np.zeros(x_fit.shape)), m, b)
  ax.plot(x_fit, unumpy.nominal_values(y_fit), color=colors[1], zorder=2)
  ax.fill_between(x_fit, unumpy.nominal_values(y_fit)-unumpy.std_devs(y_fit), unumpy.nominal_values(y_fit)+unumpy.std_devs(y_fit), fc=colors[1], ec=None, alpha=0.2, zorder=1)
  ax.set_xlim(x_fit[0], x_fit[-1])

  txt = rf"y = $({m:L}) x$  +  $({b:L})$"
  txt += "\n"
  if redchi is not None:
    txt += rf"$\chi^{{2}}_{{red}}$ = {redchi:.4g}"
  ax.text(0.1, 0.9, txt, fontsize='small', ha='left', va='top', transform=ax.transAxes)
  return fig, ax


if __name__ == '__main__':
  # Make fake data and draw.
  err = 0.2
  m, b = 1, 0
  x = np.arange(5) + 1
  y = np.random.normal(loc=m*x+b, scale=err)
  yerr = np.full(y.size, err)

  # Do fit.
  m_fit, b_fit, redchi = chisq_linear_fit(x, y, yerr, is_yerr=True, is_verbose=True)
  # m_fit, b_fit, redchi = chisq_linear_fit(x, y, yerr, is_yerr=True, vary_b=False, is_verbose=True)

  print(f"m = {m_fit}")
  print(f"b = {b_fit}")
  print(f"redchi = {redchi:.4g}")

  # Draw plot.
  plot_linear_fit(x, y, m_fit, b_fit, yerr=y)
  plt.show()