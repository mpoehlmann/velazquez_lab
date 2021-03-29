"""GC calibration calculations.
For example usage, see scripts/calc_gc_conc.py.
References:
  https://www.mksinst.com/n/flow-measurement-control-frequently-asked-questions
  https://www.mksinst.com/mam/celum/celum_assets/resources/M100B-M10MBman.pdf  (pg 32, 57)

TODO:
  correct for diffusion?
  check t configuration
"""
import copy
import numpy as np
import numericalunits as nu
import pandas as pd
import uncertainties as un

from velazquez_lab.utils import gas
from velazquez_lab.utils.gas import SCCM


def gc_conc(check, check_rate, carrier, carrier_rate, is_set_rate):
  """Calculate GC concentrations.
  Args:
    check (str): check gas name
    check_rate (float): flow rate of check gas (with units attached)
    carrier (str): carrier gas name
    carrier_rate (float): flow rate of carrier gas (with units attached)
    is_set_rate (bool): if True then input rates are set rates, if False then input rates are actual flow rates
  Returns:
    gc_mix (dict): dictionary with key being gas name and value being GC concentration
    float: corrected rate for check gas (with units attached)
    float: corrected rate for carrier gas (with units attached)
  """
  inputs = [check, carrier]
  rates = [check_rate, carrier_rate]
  corr_rates = list()
  for i, (gin, rate) in enumerate(zip(inputs, rates)):
    corr_factor = gas.gas_corr_factor(gas.mix_gasses(gin))
    corr_rates.append( rate*corr_factor if is_set_rate else rate/corr_factor )  # True: corr_rates=flow rate, False: corr_rates=set rate
    # print(f"corr_rates[{i}]: {corr_rates[gin]/SCCM} sccm")

  gc_mix = gas.mix_gasses(inputs, corr_rates)
  return gc_mix, corr_rates[0], corr_rates[1]