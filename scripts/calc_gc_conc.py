#!/usr/bin/env python3
"""Script to calculate concentrations for GC calibration."""
import uncertainties as un

from velazquez_lab.utils.gas import SCCM
from velazquez_lab.gc.gc_conc import gc_conc


def calc_gc_conc(check, check_rate, carrier, carrier_rate, is_set_rate, output_fname):
  """Calculate concentrations for GC calibration.
  Args:
    check (str): check gas name
    check_rate (float): flow rate of check gas (with units attached)
    carrier (str): carrier gas name
    carrier_rate (float): flow rate of carrier gas (with units attached)
    is_set_rate (bool): if True then input rates are set rates, if False then input rates are actual flow rates
    output_fname (str): output file name
  """


  # Do calculation
  df = gc_conc([input_1, input_2], [rate_1, rate_2], is_set_rate)
  df.to_csv(fname)
  print(f"..saving {fname}")


if __name__ == '__main__':
  """Calculate gas concentrations for GC calibration.
  To run:
    python calc_gc_conc.py
  """
  output_fname = 'gas_fracs.csv'
  is_set_rate = True

  check = 'check_0.5'
  check_rate = un.ufloat(1*SCCM, 0.01*SCCM)  # First is value, second is error

  carrier = 'CO2'
  carrier_rate = un.ufloat(100*SCCM, 1*SCCM)

  calc_gc_conc(check, check_rate, carrier, carrier_rate, is_set_rate, output_fname)









  columns = [
    'Gas',
    # 'Set flow rate for check gas (ml/min)',
    # 'Error on set flow rate for check gas (ml/min)',
    # 'Actual flow rate for check gas (ml/min)',
    # 'Error on actual flow rate for check gas (ml/min)',
    # 'Set flow rate for CO2 (ml/min)',
    # 'Error on set flow rate for CO2 (ml/min)',
    # 'Actual flow rate for CO2 (ml/min)',
    # 'Error on actual flow rate for CO2 (ml/min)',
    # 'Resulting concentration',
    # 'Error on resulting concentration',
    'Flow rate check gas (ml/min)',
    'Error on flow rate check gas (ml/min)',
    'Flow rate check gas (mol/min)',
    'Error on flow rate check gas (mol/min)',
    'Flow rate check gas (mol/s)',
    'Error on flow rate check gas (mol/s)',
    'Partial current (mA)',
    'Error on partial current (mA)',
  ]


  """
  if output_fname is not None:
    data = list()
    for g in ('H2', 'CO', 'CH4'):
      d = list()
      d.append(g)  # Gas
      d.append((rates[g]/sccm).n if is_set_rate else (corr_rates[g]/sccm).n)  # Set flow rate
      d.append((rates[g]/sccm).s if is_set_rate else (corr_rates[g]/sccm).s)  # Error on set flow rate
      d.append((rates[g]/sccm).n if not is_set_rate else (corr_rates[g]/sccm).n)  # Actual flow rate
      d.append((rates[g]/sccm).s if not is_set_rate else (corr_rates[g]/sccm).s)  # Error on actual flow rate
      d.append((rates[g]/sccm).s if not is_set_rate else (corr_rates[g]/sccm).s)  # Error on actual flow rate

      data.append(d)  # Add row


    columns = [
      # 'Gas',
      # 'Set flow rate for check gas (ml/min)',
      # 'Error on set flow rate for check gas (ml/min)',
      # 'Actual flow rate for check gas (ml/min)',
      # 'Error on actual flow rate for check gas (ml/min)',
      'Set flow rate for CO2 (ml/min)',
      'Error on set flow rate for CO2 (ml/min)',
      'Actual flow rate for CO2 (ml/min)',
      'Error on actual flow rate for CO2 (ml/min)',
      'Resulting concentration',
      'Error on resulting concentration',
      'Flow rate check gas (ml/min)',
      'Error on flow rate check gas (ml/min)',
      'Flow rate check gas (mol/min)',
      'Error on flow rate check gas (mol/min)',
      'Flow rate check gas (mol/s)',
      'Error on flow rate check gas (mol/s)',
      'Partial current (mA)',
      'Error on partial current (mA)',
    ]

    # data = np.column_stack((
    #   np.full(len(rows), set_rate_1.n/sccm),
    #   np.full(len(rows), flow_rate_1.n/sccm),
    #   np.full(len(rows), flow_rate_1.s/sccm),
    #   np.full(len(rows), set_rate_ab.n/sccm),
    #   np.full(len(rows), flow_rate_ab.n/sccm),
    #   np.full(len(rows), flow_rate_ab.s/sccm),
    #   np.array([mixture_b[g].n for g in rows]),
    #   np.array([mixture_b[g].s for g in rows]),
    # ))
    df = pd.DataFrame(data, index=rows, columns=columns)
    print(df)

    # gases = list(mixture_b.keys())
    # fracs = list(mixture_b.values())
    # frac_vals = [ f.n for f in fracs ]
    # frac_errs = [ f.s for f in fracs ]
    # df = pd.DataFrame(np.column_stack((frac_vals,frac_errs)), index=gases, columns=['Fraction', 'Error'])

    return df
    """