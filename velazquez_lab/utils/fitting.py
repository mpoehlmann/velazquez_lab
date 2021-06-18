"""Functions for fitting."""

import lmfit


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