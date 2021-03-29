"""Definition of class containing gas properties."""
from collections import namedtuple
import numericalunits as nu
import numpy as np
import pandas as pd
import uncertainties as un

FARADAY_CONST = 96485 * (nu.C/nu.mol)
SCCM = nu.cm**3 / nu.minute

Gas = namedtuple('Gas', ['cp', 'density', 'natoms', 'nelec_form'])
"""
cp: thermal capacity (specific heat) of gas
density: standard density of gas
natoms: number of atoms in one molecule of gas
nelec_form: number of electrons to form product
"""


def gas(name):
  """Get Gas object from a name."""
  if name == 'CH4':
    return Gas(cp=0.5328*(nu.smallcal/nu.g/nu.C), density=0.715*(nu.g/nu.L),  natoms=5, nelec_form=8)
  elif name == 'CO':
    return Gas(cp=0.2488*(nu.smallcal/nu.g/nu.C), density=1.250*(nu.g/nu.L),  natoms=2, nelec_form=2)
  elif name == 'CO2':
    return Gas(cp=0.2016*(nu.smallcal/nu.g/nu.C), density=1.964*(nu.g/nu.L),  natoms=3, nelec_form=None)
  elif name == 'H2':
    return Gas(cp=3.419*(nu.smallcal/nu.g/nu.C),  density=0.0899*(nu.g/nu.L), natoms=2, nelec_form=2)
  elif name == 'He':
    return Gas(cp=1.241*(nu.smallcal/nu.g/nu.C),  density=0.1786*(nu.g/nu.L), natoms=1, nelec_form=None)
  elif name == 'N2':
    return Gas(cp=0.2485*(nu.smallcal/nu.g/nu.C), density=1.25*(nu.g/nu.L),   natoms=2, nelec_form=None)
  elif name == 'O2':
    return Gas(cp=0.2193*(nu.smallcal/nu.g/nu.C), density=1.427*(nu.g/nu.L),  natoms=2, nelec_form=None)
  else:
    raise ValueError(f"Gas {name} not implemented.")


def gas_properties(gasses):
  """Return dataframe of gas properties."""
  return pd.DataFrame([gas(g) for g in gasses], columns=Gas._fields, index=gasses)


@np.vectorize
def molec_struct_factor(natoms):
  """Molecular structure correction factor of gas with n atoms (1 = monoatomic, 2 = diatomic, ...)."""
  if natoms==1:
    return 1.030
  elif natoms==2:
    return 1
  elif natoms==3:
    return 0.941
  elif natoms>=4:
    return 0.880
  else:
    raise ValueError(f"Number of atoms {natoms} is not valid.")


def gas_corr_factor(gas_fracs, cal_gas_name='N2'):
  """Gas correction factor.
  Args:
    gas_frac (dict): dictionary of gas fractions (by volume or flow rate)
    cal_gas_name (str): calibration gas name
  """
  gasses = list(gas_fracs.keys())
  fracs = np.array(list(gas_fracs.values()))
  # fracs = np.array([f.n if isinstance(f, un.UFloat) else f for f in gas_fracs.values()])
  if not np.isclose(np.array([f.n if isinstance(f, un.UFloat) else f for f in gas_fracs.values()]).sum(), 1):  # Handle values with uncertainties
    raise ValueError('The sum of volume (flow) fractions must be 1.')

  gas_props = gas_properties(gasses)
  a = fracs
  s = molec_struct_factor(gas_props['natoms'])
  d = gas_props['density']
  cp = gas_props['cp']
  cal_gas = gas(cal_gas_name)
  return (cal_gas.density*cal_gas.cp) * sum(fracs*s) / sum(a*d*cp)


def mix_gasses(inputs, rates=None):
  """Mix gases together to find new concentrations.
  Args:
    inputs (list(dict, str)): list of dictionaries of gases to mix
    rates (list(float, UFloat)): rates for each gas mixture input
  Returns:
    mixture (dict): fraction of
  """
  if not isinstance(inputs, list):  # Cast as list
    inputs = [inputs]
  if not isinstance(rates, list):  # Cast as list
    if rates is None and len(inputs)==1:
      rates = 1
    else:
      raise TypeError(f"When multiple gas line inputs are given, the rates for each must be specified.")
    rates = [rates]

  mixture = dict()
  tot_rate = 0
  for gas_fracs, rate in zip(inputs, rates):  # Loop over different gas line inputs
    tot_rate += rate
    if isinstance(gas_fracs, str):  # Prefined check gasses
      if gas_fracs == 'check_5':  # 5% check gas
        gas_fracs = { 'CO2': 0.05, 'CO': 0.05, 'CH4': 0.04, 'H2': 0.04, 'O2': 0.025, 'N2': 0.05, 'He': 0.745 }
      elif gas_fracs == 'check_1':  # 1% check gas
        gas_fracs = { 'CO2': 0.01, 'CO': 0.01, 'CH4': 0.01, 'H2': 0.01, 'O2': 0.01, 'N2': 0.95, 'He': 0 }
      elif gas_fracs == 'check_0.5':  # 0.05% check gas
        gas_fracs = { 'CO2': 0.005, 'CO': 0.005, 'CH4': 0, 'H2': 0.005, 'O2': 0.005, 'N2': 0.98, 'He': 0 }
      else:
        gas_fracs = { gas_fracs: 1 }  # Assume entirely 1 gas
    for g, frac in gas_fracs.items():  # Loop over gases for a given gas line
      val = frac * rate
      if not isinstance(val, un.UFloat):
        val = un.ufloat(val, 0)
      if g in mixture:
        mixture[g] += val
      else:
        mixture[g] = val
  for g in mixture:
    mixture[g] /= tot_rate
  return mixture


def ideal_gas_moles(p, v, t):
  """Get number of moles for ideal gas.
  Args:
    p (float): pressure (with units attached)
    v (float): volume (with units attached)
    t (float): temperature (with units attached)
  Returns:
    mol (float): number of moles (with units attached)
  """
  return (p*v) / (nu.Rgas*t)

if __name__ == '__main__':
  gasses = ['CO', 'CO2']
  print(gas_properties(gasses))