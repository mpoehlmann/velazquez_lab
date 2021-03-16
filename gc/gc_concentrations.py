"""GC calibration calculations.
References:
  https://www.mksinst.com/n/flow-measurement-control-frequently-asked-questions
  https://www.mksinst.com/mam/celum/celum_assets/resources/M100B-M10MBman.pdf
    pg 32, 57
"""
import copy
import numpy as np
import numericalunits as nu
import pandas as pd
import uncertainties as un


sccm = nu.cm**3 / nu.minute


@np.vectorize
def thermal_capacity(gas):
  """Thermal capacity (specific heat) of gas."""
  if gas=='CH4':    val = 0.5328
  elif gas=='CO':   val = 0.2488
  elif gas=='CO2':  val = 0.2016
  elif gas=='H2':   val = 3.419
  elif gas=='He':   val = 1.241
  elif gas=='N2':   val = 0.2485
  elif gas=='O2':   val = 0.2193
  else:
    raise ValueError(f"Gas {gas} not implemented.")
  units = nu.smallcal / nu.g / nu.C
  return val * units

@np.vectorize
def standard_density(gas):
  """Standard density of gas at 0C and 760 Torr."""
  if gas=='CH4':    val = 0.715
  elif gas=='CO':   val = 1.250
  elif gas=='CO2':  val = 1.964
  elif gas=='H2':   val = 0.0899
  elif gas=='He':   val = 0.1786
  elif gas=='N2':   val = 1.25
  elif gas=='O2':   val = 1.427
  else:
    raise ValueError(f"Gas {gas} not implemented.")
  units =  nu.g / nu.L
  return val * units

@np.vectorize
def natoms(gas):
  """Number of atoms in one molecule of gas."""
  if gas=='CH4':    return 5
  elif gas=='CO':   return 2
  elif gas=='CO2':  return 3
  elif gas=='H2':   return 2
  elif gas=='He':   return 1
  elif gas=='N2':   return 2
  elif gas=='O2':   return 2
  else:
    raise ValueError(f"Gas {gas} not implemented.")

@np.vectorize
def molec_struct_factor(natoms):
  """Molecular structure correction factor of gas with n atoms (1 = monoatomic, 2 = diatomic, ...)."""
  if natoms==1:    val = 1.030
  elif natoms==2:  val = 1
  elif natoms==3:  val = 0.941
  elif natoms>=4:  val = 0.880
  else:
    raise ValueError(f"Number of atoms {natoms} is not valid.")
  return val

def gas_corr_factor(gas_fracs):
  """Gas correction factor.
  Args:
    gas_frac (dict): dictionary of gas fractions (by volume or flow rate)
  """
  gas = np.array(list(gas_fracs.keys()))
  frac = list(gas_fracs.values())
  if isinstance(frac[0], un.UFloat):  # Handle values with uncertainties
    frac = np.array([f.n for f in frac])
  else:
    frac = np.array(frac)
  if not np.isclose(frac.sum(), 1):
    raise ValueError('The sum of volume (flow) fractions must be 1.')

  cal = 'N2'
  a = frac
  s = molec_struct_factor(natoms(gas))
  d = standard_density(gas)
  cp = thermal_capacity(gas)
  return (standard_density(cal)*thermal_capacity(cal)) * (a*s).sum() / (a*d*cp).sum()

def mix_gases(inputs, rates):
  """Mix gases together to find new concentrations.
  Args:
    inputs (list(dict)): list of dictionaries of gases to mix
    rates (list(UFloat)): rates for each gas mixture input
  Returns:
    mixture (dict): fraction of
  """
  mixture = dict()
  tot_rate = sum(rates)
  for i, r in zip(inputs, rates):  # Loop over different gas line inputs
    for gas, frac in i.items():  # Loop over gases for a given gas line
      frac = frac * r / tot_rate
      if gas in mixture:
        mixture[gas] += frac
      else:
        mixture[gas] = frac
  return mixture

def print_mixture(mixture, label):
  print(f"Mixture {label} (gas fractions)")
  for k, v in mixture_a.items():
    print(f"  {k}: {v}")
  print()


if __name__ == '__main__':
  """Calculate gas concentrations for GC calibration."""
  fname = 'gas_fracs.csv'

  #-------------------------
  # Vessel A
  #-------------------------
  input_1 = {
    'CO2': 0.01,
    'CO': 0.01,
    'CH4': 0.01,
    'H2': 0.01,
    'O2': 0.01,
    'N2': 0.95,
  }
  set_rate_1 = un.ufloat(1*sccm, 0.01*sccm)  # First is value, second is error

  input_2 = {
    'CO2': 1,
  }
  set_rate_2 = un.ufloat(100*sccm, 1*sccm)

  # Calculate flow rates into Vessel A
  flow_rate_1 = set_rate_1 * gas_corr_factor(input_1)
  flow_rate_2 = set_rate_2 * gas_corr_factor(input_2)
  print('flow_rate_1', flow_rate_1/sccm, 'sccm')
  print('flow_rate_2', flow_rate_2/sccm, 'sccm\n')

  # Find concentrations in first Vessel A
  mixture_a = mix_gases([input_1, input_2], [flow_rate_1, flow_rate_2])
  print_mixture(mixture_a, 'A')

  #-------------------------
  # Vessel B
  #-------------------------
  set_rate_ab = un.ufloat(30*sccm, 1*sccm)
  flow_rate_ab = set_rate_ab * gas_corr_factor(mixture_a)
  print('flow_rate_ab', flow_rate_ab/sccm, 'sccm\n')

  mixture_b = mix_gases([mixture_a], [flow_rate_ab])
  print_mixture(mixture_b, 'B')

  #-------------------------
  # Write to File
  #-------------------------
  rows = ['H2', 'CO', 'CH4']
  columns = ['set_rate_1', 'flow_rate_1', 'flow_rate_1_err', 'set_rate_2', 'flow_rate_2', 'flow_rate_2_err', 'set_rate_ab', 'flow_rate_ab', 'flow_rate_ab_err', 'mixture_b', 'mixture_b_err']
  data = np.column_stack((
    np.full(len(rows), set_rate_1.n/sccm),
    np.full(len(rows), flow_rate_1.n/sccm),
    np.full(len(rows), flow_rate_1.s/sccm),
    np.full(len(rows), set_rate_2.n/sccm),
    np.full(len(rows), flow_rate_2.n/sccm),
    np.full(len(rows), flow_rate_2.s/sccm),
    np.full(len(rows), set_rate_ab.n/sccm),
    np.full(len(rows), flow_rate_ab.n/sccm),
    np.full(len(rows), flow_rate_ab.s/sccm),
    np.array([mixture_b[g].n for g in rows]),
    np.array([mixture_b[g].s for g in rows]),
  ))
  df = pd.DataFrame(data, index=rows, columns=columns)
  print(df)

  # gases = list(mixture_b.keys())
  # fracs = list(mixture_b.values())
  # frac_vals = [ f.n for f in fracs ]
  # frac_errs = [ f.s for f in fracs ]
  # df = pd.DataFrame(np.column_stack((frac_vals,frac_errs)), index=gases, columns=['Fraction', 'Error'])

  df.to_csv(fname)
  print(f"..saving {fname}")