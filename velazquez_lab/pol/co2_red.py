"""CO2 reduction analysis."""

import matplotlib.pyplot as plt
# plt.style.use('../plot/jessica.mplstyle')
import numpy as np
import pandas as pd
import sys
import uncertainties as un
from uncertainties import unumpy as unp

from velazquez_lab.utils.file_reading import load_excel_ws
from velazquez_lab.pol import tafel_slope


"""Load liquid calibration data."""
NMR_CAL = {  # (rel area vs uM)
  'methanol': {'m': 0.0052, 'b': 0},
  'ethanol': {'m': 0.0857, 'b': 0},
  '2-propanol': {'m': 9.6212, 'b': 0},
  '1-propanol': {'m': 58.22, 'b': 0},
  '1-propanol': {'m': 58.22, 'b': 0},
  'butanol': {'m': 49.839, 'b': 0},
  'acetone': {'m': 0.0083, 'b': 0},
  'formate': {'m': 0.0053, 'b': 0},
  'ethylene glycol': {'m': 0.0089, 'b': 0},
  'acetate': {'m': 0.0072, 'b': 0},
}


def get_median_current(t, i, intervals):
  median_current= []
  t = t - min(t)
  intervals = np.asarray(intervals)
  for idx, imax in enumerate(intervals):
    imin = 0 if idx == 0 else intervals[idx - 1]
    mask = (t>=imin) & (t<imax)
    med = np.median(i[mask])
    median_current.append(med)
  return np.array(median_current)


def get_fe_pct(precursor, product, conc_from_red, solution_vol, coulombs_passed):
  """Calculate faradaic efficiency (in percentage).
  Args:
    precursor (str): Precursor name. Choose from: 'CO', 'CO2'.
    product (str): Product name.
    conc_from_red (float): Concentration of product from CO2 reduction.
    solution_vol (float): Solution volume in mL.
  """
  ELEC_TO_REDUCE = {
    'CO': {
      'methanol': 4,
      'ethanol': 10,
      '2-propanol': 16,
      '1-propanol': 16,
      'butanol': 20,
      'acetone': 14,
      'formate': None,
      'ethylene glycol': 8,
      'acetate': 6,
    },
    'CO2': {
      'methanol': 6,
      'ethanol': 12,
      '2-propanol': 18,
      '1-propanol': 18,
      'butanol': 22,
      'acetone': 16,
      'formate': 2,
      'ethylene glycol': 10,
      'acetate': 8,
    },
  }
  elec_to_reduce = ELEC_TO_REDUCE[precursor][product]
  if elec_to_reduce is None:
    return 0

  mol_produced = (conc_from_red/1000000) * (solution_vol/1000)  # mol
  coulombs_from_precursor = (mol_produced*elec_to_reduce) * 96485  # C
  return 100 * coulombs_from_precursor / coulombs_passed


def liquid_product_analysis(precursor, products, integs, dmf_right_peaks, dmf_left_peaks, solution_vol, coulombs_passed, current, area):
  """Calculate faradaic efficiency for liquid."""
  rows = []
  for i, prod in enumerate(products):
    prod = prod.lower()
    integ = {key: integs[key].iloc[i] for key in integs.keys()}
    rel_area = {key: _integ / dmf_left_peaks[key] if prod=='formate' else _integ / dmf_right_peaks[key] for key, _integ in integ.items()}
    conc = {key: (_rel_area-NMR_CAL[prod]['b'])/NMR_CAL[prod]['m'] for key, _rel_area in rel_area.items()}  # uM
    conc_from_red = conc['run'] - conc['blank']
    fe_pct = {pre: get_fe_pct(pre, prod, conc_from_red, solution_vol, coulombs_passed) for pre in ['CO', 'CO2']}
    partial_current_density = (current / area) * (fe_pct['CO2'] / 100)  # mA/cm2

    rows.append([prod, integ['blank'], integ['run'], rel_area['blank'], rel_area['run'], conc['blank'], conc['run'], fe_pct['CO'], fe_pct['CO2'], partial_current_density])
    # print(rows[-1])
    # break

  df = pd.DataFrame(rows, columns=['product', 'integ_blank', 'integ_run', 'rel_area_blank', 'rel_area_run', 'conc_blank', 'conc_run', 'fe_pct_CO', 'fe_pct_CO2', 'partial_current_density'])
  return df


def gaseous_product_analysis(peak_areas, gc_calib_curve, median_current, area):
  """
  Args:
    peak_areas (dict): Peak areas (in mV/min) for each gas product.
    gc_calib_curve (dict): GC calibration curve slopes (mV/min/mA) and intercepts (in mV/min).
  """
  rows = []
  for key, _peak_area in peak_areas.items():
    current = (_peak_area - gc_calib_curve[key]['b']) / gc_calib_curve[key]['m']  # mA
    fe_pct = 100 * (current / median_current)
    partial_current_density = current / area  # mA/cm2

    rows.append([key, _peak_area, current, fe_pct, partial_current_density])

  df = pd.DataFrame(rows, columns=['product', 'peak_area', 'current', 'fe_pct', 'partial_current_density'])
  return df


if __name__ == "__main__":
  """Run CO2 reduction analysis.
  To run:
    python co2_red.py
  Notes:
    Time intervals don't match.
  """
  excel_file = pd.ExcelFile('/Users/michael/Downloads/FE_imput.xlsx')
  echem_data = pd.read_table('../../data/co2_red/CP_-20mA_ptfe_03_CP_C03.txt')

  """Load workbook."""
  wb = {sheet: load_excel_ws(excel_file, sheet) for sheet in excel_file.sheet_names}
  nmr_data = wb['NMR']
  gc_data = wb['GC_chi-squared']

  """Get inputs."""
  gc_time_intervals = gc_data.loc[3:14, 'B'].dropna() * 60  # s
  area_geometric = nmr_data.loc[2, 'W']  # cm2
  solution_vol = nmr_data.loc[2, 'T']  # mL
  coulombs_passed = nmr_data.loc[2, 'U']  # C
  ph = nmr_data.loc[2, 'X']
  ru = nmr_data.loc[2, 'Y']  # Ohms

  """Median current."""
  median_current = get_median_current(echem_data['time/s'], echem_data['I/mA'], gc_time_intervals)  # Amps
  print(f"gc time intervals: {gc_time_intervals}")
  print(f"median currents: {median_current}")
  print(f"overall mediancurrent: {np.median(echem_data['I/mA'])}")

  """Liquid product analysis (NMR)."""
  liq_df = liquid_product_analysis(
    precursor='CO2',
    products=nmr_data.loc[4:12, 'A'],
    integs={'blank': nmr_data.loc[4:12, 'E'], 'run': nmr_data.loc[4:12, 'F']},
    dmf_right_peaks={'blank': nmr_data.loc[2, 'E'], 'run': nmr_data.loc[2, 'F']},
    dmf_left_peaks={'blank': nmr_data.loc[3, 'E'], 'run': nmr_data.loc[3, 'F']},
    solution_vol=solution_vol,  # mL
    coulombs_passed=coulombs_passed,  # C
    current=np.median(echem_data['I/mA']),  # mA
    area=area_geometric,
  )
  print()
  print(f'liq_df:\n{liq_df}')

  """Gaseous product analysis (GC)."""
  peak_areas = {  # mV/min
    'CO': gc_data.loc[3:14, 'C'].dropna(),
    'methane': gc_data.loc[3:14, 'D'].dropna(),
    'hydrogen': gc_data.loc[3:14, 'E'].dropna(),
  }

  gc_calib_curve = {  # m: mV/min/mA, b: mV/min
    'CO': {'m': un.ufloat(gc_data.loc[3, 'S'], gc_data.loc[3, 'T']), 'b': un.ufloat(gc_data.loc[3, 'U'], gc_data.loc[3, 'V'])},
    'methane': {'m': un.ufloat(gc_data.loc[4, 'S'], gc_data.loc[4, 'T']), 'b': un.ufloat(gc_data.loc[4, 'U'], gc_data.loc[4, 'V'])},
    'hydrogen': {'m': un.ufloat(gc_data.loc[5, 'S'], gc_data.loc[5, 'T']), 'b': un.ufloat(gc_data.loc[5, 'U'], gc_data.loc[5, 'U'])},
  }

  gas_df = gaseous_product_analysis(peak_areas, gc_calib_curve, median_current=median_current, area=area_geometric)
  print()
  print(f'gas_df:\n{gas_df.head()}')

  """Calculate polarization curve quantities."""
  potential_fixed = tafel_slope.corrected_potential(echem_data['<Ewe>/V'], echem_data['I/mA'], ph, ru)

  """Plot: raw current vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(echem_data['time/s']/60, echem_data['I/mA'])
  ax.set(xlabel='Time (min)', ylabel='Current (mA)')

  """Plot: raw current density vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(echem_data['time/s']/60, echem_data['I/mA']/area_geometric)
  ax.set(xlabel='Time (min)', ylabel='Current density (mA/cm2)')

  """Plot: liquid partial current density."""
  fig, ax = plt.subplots(constrained_layout=True)
  liq_prod_mask = ( np.abs(unp.nominal_values(liq_df['partial_current_density'])) > 0 )
  ax.bar(liq_df['product'][liq_prod_mask], np.abs(unp.nominal_values(liq_df['partial_current_density'][liq_prod_mask])))
  plt.xticks(rotation=45, horizontalalignment="right")
  ax.set(ylabel='Partial current density (mA/cm2)', title='Liquid products')

  """Plot: gaseous partial current density vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  for i, prod in enumerate(gas_df['product']):
    ax.errorbar(gc_time_intervals, unp.nominal_values(gas_df['partial_current_density'].iloc[i]), yerr=unp.std_devs(gas_df['partial_current_density'].iloc[i]), fmt='o-', label=prod)
    ax.set(xlabel='Time (s)', ylabel='Partial current density (mA/cm2)', title='Gas products')
  ax.legend()

  """Plot: liquid faradaic efficiency."""
  fig, ax = plt.subplots(constrained_layout=True)
  ax.bar(liq_df['product'][liq_prod_mask], np.abs(unp.nominal_values(liq_df['fe_pct_CO2'][liq_prod_mask])))
  plt.xticks(rotation=45, horizontalalignment="right")
  ax.set(ylabel='CO2 Faradaic efficiency (%)', title='Liquid products')

  """Plot: gaseous faradaic efficiency vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  for i, prod in enumerate(gas_df['product']):
    ax.errorbar(gc_time_intervals, np.abs(unp.nominal_values(gas_df['fe_pct'].iloc[i])), yerr=unp.std_devs(gas_df['fe_pct'].iloc[i]), fmt='o-', label=prod)
    ax.set(xlabel='Time (s)', ylabel='Faradaic efficiency (%)', title='Gas products')
  ax.legend()

  """Plot: raw potential vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(echem_data['time/s']/60, echem_data['<Ewe>/V'])
  ax.set(xlabel='Time (min)', ylabel='Potential (V) vs Ag/AgCl')

  """Plot: fixed potential (only ru) vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(echem_data['time/s']/60, echem_data['<Ewe>/V']-0.15*ru*(echem_data['I/mA']/1000))
  ax.set(xlabel='Time (min)', ylabel='Potential (V) corrected with Ru')

  """Plot: fixed potential vs. time."""
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(echem_data['time/s']/60, potential_fixed)
  ax.set(xlabel='Time (min)', ylabel='Potential (V) vs RHE')

  plt.show()


  # Print median values