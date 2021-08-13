"""Fit polarization curves to find Tafel slope."""

import argparse
import numpy as np
import pandas as pd

import velazquez_lab.pol.julius as jl
import velazquez_lab.utils.linear_fitting as ft


def load_data(file):
  """Load data.
  Args:
    file: FIXME
  """
  df = pd.read_table(file, sep='\t', header=(0), usecols=[0, 1])
  df = df.rename(columns={df.columns[0]: 'E', df.columns[1]: 'I'})
  return df


def correct_potential(potential, current, ph, ru=0):
  """Correct potential from Ag/AgCl reference to RHE.
  Args:
    potential (array_like): FIXME
    current (array_like): FIXME
    ph (float): pH level between 0 and 14.
    ru (float): uncompensated resistance in UNITS (FIXME).
  """
  potential_fixed = potential + 0.210 + 0.059*ph - current*(ru/1000.)
  return potential_fixed


# def fit_tafel_slope_bayesian(log_currents, voltages, model='co2', sigma=0.1, nsamples=2500):
#   """Fit Tafel slope using Bayesian methods with the julius package.
#   This is used in fit_tafel_slope().
#   Args:
#     log_currents (np.ndarray): FIXME
#     voltages (np.ndarray): FIXME
#     model (str): Fit model to use. Choose from 'co2' or 'her'. FIXME
#     sigma (float): relative error on experimental measurements
#     nsamples (int): FIXME
#   Returns:
#     FIXME
#   Reference:
#     FIXME
#   Notes:
#     The julius models have issues when all the y data is negative.
#     For now just shift all the data so it is uniformly positive.
#   """
#   offset = np.min(log_currents)
#   _log_currents = log_currents - offset

#   if model == 'co2':
#     frozen_params = None  # No frozen parameters in this model
#     fit_model = jl.models.series_resistances_model  # Set up the simple model and the probabilistic model for series resistances
#     bayes_model = jl.models.series_resistances_model_bayes
#     pname_map = jl.models.series_resistances_model_bayes.name_to_index_map
#     guess = (15, 2, 15)  # An initial guess that was manually tuned (by the authors), helps to converge fits quickly on the first guess
#   else:
#     raise ValueError(f"Tafel slope model not implemented: {model}.")

#   """Do fitting."""
#   result = jl.fits.fit_bayes_with_preconditioned_bounds(
#     voltages,
#     _log_currents,
#     fit_model,
#     bayes_model,
#     sigma,
#     frozen_params,
#     nsamples=nsamples,
#     guess=guess
#   )

#   """Construct the mean a posteriori model from the Bayes traces."""
#   mean_ap_model = jl.fits.collapsed_simple_model_from_bayes_model(
#     result,
#     fit_model,
#     frozen_params,
#     pname_map
#   )

#   """Prepare output."""
#   d_voltages, d_voltages_offset = jl.visualization.densely_sample_array(voltages)
#   ap_model_data = mean_ap_model(d_voltages_offset)
#   ap_tafels = jl.visualization.uxform_v_per_e_to_mv_per_dec(result.get_values('alpha'))

#   """Draw plots."""
#   jl.visualization.three_panel_fit_examination_plot(
#     voltages,
#     log_currents,
#     result,
#     mean_ap_model,
#     # reported_tafel=record.r_tafel,
#     cutoff_fits=None,
#     fname=None,
#     interactive=True
#   )

#   return np.mean(ap_tafels), d_voltages, ap_model_data+offset


def fit_tafel_slope_lsq(voltages, log_currents, model='co2'):
  """Fit the Tafel slope using least squares regression.
  Args:
    voltages (array_like): Potentials (in V).
    log_currents (array_like): Log10 of currents.
    method (str): Tafel slope fitting method. Choose from 'simple' or 'bayesian'.
    model (str): Fit model to use. Choose from 'co2' or 'her'. FIXME
  Returns:
    tafel_slope (float): Tafel slope (in mV/decade).
    rsq (float): R-squared value.
    res_voltages (array_like): Potentials (in V) for plotting fit result.
    res_log_currents (array_like): Log10 o currents for plotting fit result.
  """
  if model == 'co2':
    fitresult, optvals = ft.linear_fit(voltages, log_currents)
    tafel_slope = np.abs(1000/optvals['m'])  # 1000 to convert V to mV.
    res_voltages = voltages
    res_log_currents = ft.linear_eqn(voltages, **optvals)
    rsq = 1 - fitresult.residual.var() / np.var(voltages)
  else:
    raise ValueError(f"Tafel slope model not implemented: {model}.")
  return tafel_slope, rsq, res_voltages, res_log_currents


if __name__ == '__main__':
  """Example Tafel slope analysis."""
  import matplotlib.pyplot as plt

  """Define data (023 from julius)."""
  e = np.array([-1.7993623470309288, -1.8245174641594426, -1.850406759706475, -1.8740394072459903, -1.900699443881786, -1.9258355484217726, -1.9509614154140908, -2.0003517328877565, -2.0512191822393175, -2.1005261368248247, -2.2020401969996675, -2.3012127837720247])
  log_i = np.array([-0.34146608995148126, -0.1367114803128301, 0.03715864176992567, 0.23225339392986533, 0.42350175318003813, 0.6031597459625669, 0.7693041758225686, 0.964523241061341, 1.109556385121918, 1.1947364379915393, 1.1932958687838893, 1.1011104082953382])
  mask = (log_i<1)

  """Least-squares fitting."""
  lsq_res = dict()
  lsq_res['tafel_slope'], lsq_res['rsq'], lsq_res['e'], lsq_res['log_i'] = fit_tafel_slope_lsq(e[mask], log_i[mask])
  print(f"Tafel slope (lsq): {lsq_res['tafel_slope']} mV/decade")

  """Bayesian fitting."""
  bay_res = dict()
  # bay_res['tafel_slope'], bay_res['rsq'], bay_res['e'], bay_res['log_i'] = fit_tafel_slope_bayesian(e[mask], log_i[mask])
  # print(f"Tafel slope (bayesian): {bay_res['tafel_slope']} mV/decade")

  """Plot fit results"""
  fig, ax = plt.subplots()
  ax.set(ylabel="Potential (V)", xlabel=r"log$_{10}$(Current)")
  ax.plot(log_i, e, 'o', label='data')
  ax.plot(lsq_res['log_i'], lsq_res['e'], label='least squares')
  # ax.plot(bay_res['log_i'], bay_res['e'], label='bayesian')
  ax.legend()
  plt.show()