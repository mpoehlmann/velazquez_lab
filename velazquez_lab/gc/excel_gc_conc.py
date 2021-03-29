"""Excel interface for GC concentration calculations."""
import numericalunits as nu
import uncertainties as un
# import xlwings as xw

import velazquez_lab.gc.gc_conc as gc
from velazquez_lab.utils.gas import FARADAY_CONST, gas, ideal_gas_moles, SCCM


# @xw.func
# @xw.arg('gas_comp', str)
# @xw.arg('check', str)
# @xw.arg('check_rate_val', float)
# @xw.arg('check_rate_err', float)
# @xw.arg('carrier', str)
# @xw.arg('carrier_rate_val', float)
# @xw.arg('carrier_rate_err', float)
# @xw.arg('is_set_rate', bool)
def excel_gc_conc(gas_comp, check, check_rate_val, check_rate_err, carrier, carrier_rate_val, carrier_rate_err, is_set_rate):
  """Excel interface for GC concentration calculations.
  Args:
    gas_comp (str): name of gas component in check gas for which concentrations are returned
    check (str): check gas name
    check_rate_val (float): flow rate of check gas in SCCM
    check_rate_err (float): error on flow rate of check gas in SCCM
    carrier (str): carrier gas name
    carrier_rate_val (float): flow rate of carrier gas in SCCM
    carrier_rate_err (float): error on flow rate of carrier gas in SCCM
    is_set_rate (bool): if True then input rates are set rates, if False then input rates are actual flow rates
  """
  check_rate = un.ufloat(check_rate_val*SCCM, check_rate_err*SCCM)
  carrier_rate = un.ufloat(carrier_rate_val*SCCM, carrier_rate_err*SCCM)
  gc_mix, check_rate_corr, carrier_rate_corr = gc.gc_conc(check, check_rate, carrier, carrier_rate, is_set_rate)

  # Collect some values
  rates = {
    'check': {
      'set': check_rate if is_set_rate else check_rate_corr,
      'flow': check_rate if not is_set_rate else check_rate_corr,
    },
    'carrier': {
      'set': carrier_rate if is_set_rate else carrier_rate_corr,
      'flow': carrier_rate if not is_set_rate else carrier_rate_corr,
    }
  }
  gas_comp_frac = gc_mix[gas_comp]
  tot_flow_rate = rates['check']['flow'] + rates['carrier']['flow']
  gas_comp_flow_rate = gas_comp_frac * tot_flow_rate
  gas_comp_flow_rate_molar = ideal_gas_moles(1*nu.atm, gas_comp_flow_rate, 293*nu.K)

  # Create output in desired format
  data = list()

  # Set and flow rates
  for key in ('check', 'carrier'):
    for rt in ('set', 'flow'):
      data.append((rates[key][rt]/SCCM).n)  # Value
      data.append((rates[key][rt]/SCCM).s)  # Error

  # Resulting concentration: specified gas
  data.append(gas_comp_frac.n)  # Value
  data.append(gas_comp_frac.s)  # Error

  # Resulting flow rate (ml/min): specified gas
  data.append((gas_comp_flow_rate/SCCM).n)  # Value
  data.append((gas_comp_flow_rate/SCCM).s)  # Error

  # Resulting flow rate (mol/s): specified gas
  data.append((gas_comp_flow_rate_molar/(nu.mol/nu.s)).n)  # Value
  data.append((gas_comp_flow_rate_molar/(nu.mol/nu.s)).s)  # Error

  # Partial current (mA): specified gas
  val = gas_comp_flow_rate_molar * FARADAY_CONST * gas(gas_comp).nelec_form
  data.append((val/nu.mA).n)  # Value
  data.append((val/nu.mA).s)  # Error

  return data


if __name__ == '__main__':
  data = excel_gc_conc('H2',
    'check_1', 1, 0.01,
    'CO2', 200, 2,
    True
    )

  print(data)