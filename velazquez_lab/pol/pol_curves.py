"""Fit polarization curves to find Tafel slope."""

from struct import unpack
import numpy as np
import pandas as pd

from velazquez_lab.pol.julius import fits
from velazquez_lab.pol.julius import models
from velazquez_lab.pol.julius import visualization
from velazquez_lab.utils import fitting


def load_data(file):
  """Load data."""
  df = pd.read_csv(file, sep='\t', header=(0))
  df = df.rename(columns={df.columns[0]: 'E', df.columns[1]: 'I'})
  df['E'] = np.abs(df['E'])
  df['I'] = np.abs(df['I'])
  return df


def correct_potential(df, ph, ru=0):
  # Fixed potential
  potential_fixed = df['E'] + 0.210 + 0.059*ph - df['I']*(ru/1000.)
  df.insert(1, 'E_fixed', potential_fixed)
  return df


def fit_tafel_slope_julius(voltages, currents, sigma=0.1, nsamples=2500, verbose=True, draw=False):
  """Fit Tafel slope using julius package.
  Args:
    voltages (np.ndarray):
    log_currents (np.ndarray):
    sigma (float): relative error on experimental measurements
    nsamples (int):
    verbose (bool): if True then prints detailed information
    draw (bool): if True then draws fit result plots
  """
  # The model has issues when all the y data is negative; for now just shift all the data so it is uniformly positive
  log_currents = np.log10(currents)
  offset = np.min(log_currents)
  log_currents = log_currents - offset

  # Setup models
  frozen_params = None  # No frozen parameters in this model
  simple_model = models.series_resistances_model  # Set up the simple model and the probabilistic model for series resistances
  bayes_model = models.series_resistances_model_bayes
  pname_map = models.series_resistances_model_bayes.name_to_index_map
  guess = (15, 2, 15)  # An initial guess that was manually tuned (by the authors), helps to converge fits quickly on the first guess

  # Do fitting
  result = fits.fit_bayes_with_preconditioned_bounds(
    voltages,
    log_currents,
    simple_model,
    bayes_model,
    sigma,
    frozen_params,
    nsamples=nsamples,
    guess=guess
  )

  # Construct the mean a posteriori model from the Bayes traces
  mean_ap_model = fits.collapsed_simple_model_from_bayes_model(
    result,
    simple_model,
    frozen_params,
    pname_map
  )

  # Draw plots
  if draw:
    visualization.three_panel_fit_examination_plot(
      voltages,
      log_currents,
      result,
      mean_ap_model,
      # reported_tafel=record.r_tafel,
      cutoff_fits=None,
      fname=None,
      interactive=True
    )

  # Prepare output
  d_voltages, d_voltages_offset = visualization.densely_sample_array(voltages)
  ap_model_data = mean_ap_model(d_voltages_offset)
  ap_tafels = visualization.uxform_v_per_e_to_mv_per_dec(result.get_values('alpha'))
  return np.mean(ap_tafels), d_voltages, ap_model_data+offset


def fit_tafel_slope_linear(voltages, currents):
  log_currents = np.log10(currents)
  fitresult, optvals = fitting.linear_fit(voltages, log_currents)
  m, b = optvals['m'], optvals['b']
  rsq = 1 - fitresult.residual.var() / np.var(log_currents)
  return m, voltages, fitting.linear_eqn(voltages, m, b)

if __name__ == '__main__':
  import matplotlib.pyplot as plt

  # e = np.array([0.60284483, 0.60610604, 0.6094408, 0.6127544, 0.61609769, 0.61959791, 0.62320405, 0.62642354, 0.62979329, 0.63311261, 0.63644254, 0.63980734, 0.64309675, 0.64639366, 0.64981765, 0.65310133, 0.65641838, 0.65986711, 0.66318315, 0.66643566, 0.66973549, 0.67315614, 0.67641705, 0.67985791, 0.68305719, 0.68647254, 0.68975431, 0.69302344, 0.69636506, 0.69889098, 0.70012534])
  # i = np.array([7.878262157431934, 8.306836020061048, 8.775572170466972, 9.229538619101078, 9.707198713473105, 10.21525538974012, 10.7280598002888, 11.25139176009338, 11.81990910134856, 12.35147648743373, 12.9043798398355, 13.50373173022009, 14.20802145937529, 14.79618116311059, 15.38983181208488, 15.97151124714162, 16.58803395828576, 17.20761123827235, 17.8377430226729, 18.4680258380381, 19.10381641132739, 19.75650748357964, 20.42134625526003, 21.10311477659783, 21.76537715704594, 22.49228847443599, 23.19783165179788, 23.91230228503255, 24.60107213348023, 25.1165502338729, 25.31827992891016])
  # mask = np.ones(e.shape, dtype=bool)
  # mask = (e<0.64)

  # 023 (real data from another paper)
  # e = np.abs(np.array([-1.7993623470309288, -1.8245174641594426, -1.850406759706475, -1.8740394072459903, -1.900699443881786, -1.9258355484217726, -1.9509614154140908, -2.0003517328877565, -2.0512191822393175, -2.1005261368248247, -2.2020401969996675, -2.3012127837720247]))
  # i = 10**np.array([-0.34146608995148126, -0.1367114803128301, 0.03715864176992567, 0.23225339392986533, 0.42350175318003813, 0.6031597459625669, 0.7693041758225686, 0.964523241061341, 1.109556385121918, 1.1947364379915393, 1.1932958687838893, 1.1011104082953382])
  # mask = (e<2)

  # 135
  e = np.array([-0.024096385542168752, 0.01807228915662651, 0.06626506024096379, 0.12048192771084332, 0.17469879518072284, 0.2168674698795181, 0.2710843373493974])
  i = np.array([1.8782051055441147, 2.871445373502012, 5.605357959361029, 10.52801193767423, 16.514943603663948, 23.373033621957834, 30.230611170608626])
  # mask = (e<0.2)
  mask = np.ones(e.shape, dtype=bool)

  # simulated data from bayesian paper
  # e = np.array([0.05, 0.07055393586005831, 0.09023323615160352, 0.1099125364431487, 0.13046647230320702, 0.1501457725947522, 0.1698250728862974, 0.19562682215743443, 0.22142857142857142, 0.24723032069970846, 0.2725947521865889, 0.29839650145772595, 0.324198250728863, 0.35000000000000003])
  # i = 10**np.array([-2.2193675889328066, -2.0007905138339925, -1.807114624505929, -1.6936758893280635, -1.5276679841897236, -1.4363636363636365, -1.3948616600790515, -1.347826086956522, -1.3173913043478263, -1.3256916996047434, -1.3229249011857709, -1.2758893280632413, -1.2703557312252967, -1.3284584980237155])
  # mask = np.ones(e.shape, dtype=bool)
  # mask = (e<0.15)

  # df = load_data('/Users/michael/Downloads/2-6-2021_K2Mo6S6_sample1_her_12_LSV_C02_log_fit.txt')
  # e = df['E'].to_numpy()
  # i = 10 ** (-1*df['I'].to_numpy())
  # mask = np.ones(e.shape, dtype=bool)

  jm, jres_x, jres_y = fit_tafel_slope_julius(e, i)
  # jm, jres_x, jres_y = fit_tafel_slope_julius(e[mask], i[mask])
  lm, lres_x, lres_y = fit_tafel_slope_linear(e[mask], i[mask])

  print()
  print(f"Tafel slope (Bayesian): {jm} mV/decade")
  print(f"Tafel slope (Linear): {1000/lm} mV/decade")

  fig, ax = plt.subplots()
  ax.set(xlabel="Potential (V)", ylabel=r"log$_{10}$ ( Current )")
  ax.plot(e, np.log10(i), 'o', label='data')
  ax.plot(jres_x, jres_y, label='bayesian')
  ax.plot(lres_x, lres_y, label='linear')
  ax.legend()
  plt.show()