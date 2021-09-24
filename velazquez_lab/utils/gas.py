"""Definition of class containing gas properties."""
from collections import namedtuple
import numericalunits as nu
import numpy as np
import pandas as pd
import uncertainties as un
from uncertainties import unumpy as unp

FARADAY_CONST = 96485 * (nu.C/nu.mol)
SCCM = nu.cm**3 / nu.minute

"""
cp: thermal capacity (specific heat) of gas
density: standard density of gas
natoms: number of atoms in one molecule of gas
nelec_form: number of electrons to form product
"""
GASES = pd.DataFrame.from_dict({
  'CH4': dict(cp=0.5328*(nu.smallcal/nu.g/nu.C), density=0.715*(nu.g/nu.L),  natoms=5, nelec_form=8),
  'CO': dict(cp=0.2488*(nu.smallcal/nu.g/nu.C), density=1.250*(nu.g/nu.L),  natoms=2, nelec_form=2),
  'CO2': dict(cp=0.2016*(nu.smallcal/nu.g/nu.C), density=1.964*(nu.g/nu.L),  natoms=3, nelec_form=0),
  'H2': dict(cp=3.419*(nu.smallcal/nu.g/nu.C),  density=0.0899*(nu.g/nu.L), natoms=2, nelec_form=2),
  'He': dict(cp=1.241*(nu.smallcal/nu.g/nu.C),  density=0.1786*(nu.g/nu.L), natoms=1, nelec_form=0),
  'N2': dict(cp=0.2485*(nu.smallcal/nu.g/nu.C), density=1.25*(nu.g/nu.L),   natoms=2, nelec_form=0),
  'O2': dict(cp=0.2193*(nu.smallcal/nu.g/nu.C), density=1.427*(nu.g/nu.L),  natoms=2, nelec_form=0),
})

GAS_MIXTURES = {
  # 5% check gas
  'check_5': { 'CO2': 0.05, 'CO': 0.05, 'CH4': 0.04, 'H2': 0.04, 'O2': 0.025, 'N2': 0.05, 'He': 0.745 },
  # 1% check gas
  'check_1': { 'CO2': 0.01, 'CO': 0.01, 'CH4': 0.01, 'H2': 0.01, 'O2': 0.01, 'N2': 0.95, 'He': 0 },
  # 0.05% check gas
  'check_0.5': { 'CO2': 0.005, 'CO': 0.005, 'CH4': 0, 'H2': 0.005, 'O2': 0.005, 'N2': 0.98, 'He': 0 } ,
}

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


def gas_corr_factor(gas_fracs, ref_gas_name='N2'):
  """Get the gas correction factor.
  Args:
    fracs (pd.Series): gas fractions (by volume or flow rate) with index being the gase name
    ref_gas_name (str): reference gas name
  """
  gas_names = gas_fracs.index
  a = gas_fracs  # Gas fractions
  s = molec_struct_factor(GASES.loc['natoms', gas_names])
  d = GASES.loc['density', gas_names]
  cp = GASES.loc['cp', gas_names]
  ref_gas = GASES[ref_gas_name]
  corr = (ref_gas['density']*ref_gas['cp']) * sum(gas_fracs * s) / sum(a * d * cp)
  return corr


def mix_gases(gas_names, actual_rates):
  """Mix gases together to find new concentrations.
  Args:
    gas_names (list): list of gases to mix
    actual_rates (list): rates for each gas mixture input
  Returns:
    mixture (dict): fraction of
  """
  # Do some setup for inputs.
  if isinstance(gas_names, str):
    gas_names = [gas_names]
    actual_rates = [actual_rates]

  # Combine the gases.
  final_mix_rates = dict()
  for _gas_name, _actual_rate in zip(gas_names, actual_rates):
    # Fractions of each gas for the input.
    if _gas_name in GAS_MIXTURES:
      input_fracs = GAS_MIXTURES[_gas_name]
    elif _gas_name in GASES:
      input_fracs = {_gas_name: 1}
    else:
      raise ValueError(f"Gas not implemented: {_gas_name}")

    # Add the flow rate of the gas components to the final mixture.
    for g, frac in input_fracs.items():
      if g not in final_mix_rates:  # Add new gas to final mixture if not already present.
        final_mix_rates[g] = un.ufloat(0, 0)
      final_mix_rates[g] += frac * _actual_rate

  tot_rate = sum(final_mix_rates.values())
  final_mix_fracs = pd.Series({g: rate/tot_rate for g, rate in final_mix_rates.items()})
  return final_mix_fracs


def ideal_gas_moles(p, v, t):
  """Get number of moles for ideal gas.
  Args:
    p (float): pressure (with units attached)
    v (float): volume (with units attached)
    t (float): temperature (with units attached)
  Returns:
    mol (float): number of moles (with units attached)
  """
  return (p * v) / (nu.Rgas * t)


if __name__ == '__main__':
  print(GASES)

  final_mix_fracs = mix_gases(['check_0.5', 'CO2'], [2, 28])
  print(final_mix_fracs)