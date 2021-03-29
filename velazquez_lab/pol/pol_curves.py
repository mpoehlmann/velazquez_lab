"""Create polarization curves."""

import matplotlib.pyplot as plt
import numpy as np

from ecsa import do_linear_fit, calculate_ecsa, colors


def make_pol_curves(log, input_fname, ph, gsa, ecsa, ru=None, x_range=None, y_range=None):
  """Create polarization curves.
  Args:
    input_fname (str): input file name
    ph (float): pH level
    gsa (float): geometric surface area
    ru (float or None): uncompensated resistance in UNITS, if None then e_fixed is calculated without this
    x_range: if None then user input is prompted
    y_range: if None then user input is prompted
  """
  output = {}

  # Load text file
  log.write(f'\n\nPolarization curve file name:\n  {input_fname}')

  potential, current = np.loadtxt(input_fname, delimiter='\t', unpack=True, skiprows=1)
  pt_mask = (current!=0)  # Make sure no zeros are used in log
  potential, current = potential[pt_mask], current[pt_mask]

  # Fixed potential
  if ru is None:  # Don't use uncompensated resistance
    potential_fixed = potential + 0.210 + 0.059*ph
  else:  # Correct with uncompensated resistance
    potential_fixed = potential + 0.210 - current*(ru/1000.) + 0.059*ph

  # Fixed current
  current_corr = {
    'GSA': current / gsa,
    'ECSA': current / ecsa
  }

  output['E'] = potential
  output['I'] = current
  output['E(RHE)'] = potential_fixed
  for key,val in current_corr.items():
    output[f'I/{key}'] = val

  fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10,8), constrained_layout=True)
  x_tafel, y_tafel = [ {} for _ in range(2) ]
  a = 0
  for const,rt in zip([gsa,ecsa],['GSA','ECSA']):
    # Plot ECSA or GSA corrected current vs. fixed potential
    axes[0,a].set(xlabel='Fixed Potential', ylabel=f'I / {rt}', xlim=[min(potential_fixed),0])
    axes[0,a].plot(potential_fixed, current_corr[rt], c=colors[a])

    # Output potential at I/GSA=10 or I/ECSA=-10
    # val_at_10 = np.interp(-10, current_corr[rt], potential_fixed, left=np.NaN, right=np.NaN)
    srt_idx = current_corr[rt].argsort()
    srt_curr, srt_pot = current_corr[rt][srt_idx], potential_fixed[srt_idx]
    _xval = -10
    if srt_curr[0] > _xval:
      log.write('Potential at I/{rt} = -10: data all greater than -10')
    else:
      _tmp = 0
      while True:
        if srt_curr[_tmp] > _xval:
          _x0, _y0 = srt_curr[_tmp], srt_pot[_tmp]
          _x1, _y1 = srt_curr[_tmp-1], srt_pot[_tmp-1]
          val_at_10 = _y0 + (_xval-_x0)*(_y1-_y0)/(_x1-_x0)
          log.write(f'Potential at I/{rt} = -10: {val_at_10}')
          break
        if _tmp == srt_curr.size - 1:
          log.write('Potential at I/{rt} = -10: data all less than -10')
          break
        _tmp += 1
    # log.write(f'Potential at I/{rt} = -10: {val_at_10}')

    # Tafel slope
    x_tafel[rt] = np.log10(np.abs(current_corr[rt]))
    y_tafel[rt] = np.abs(potential_fixed)

    # Plot overpotential vs. log(I/GSA or I/ECSA)
    axes[1,a].set(xlabel=f'log10(abs(I/{rt})', ylabel='Overpotential')
    axes[1,a].plot(x_tafel[rt], y_tafel[rt], c=colors[a])

    output[f'I_Tafel_{rt}'] = x_tafel[rt]
    output[f'E_Tafel_{rt}'] = y_tafel[rt]

    a += 1

  # Fit Tafel slopes (user input for range)
  plt.show(block=False)

  is_redo = False
  fig, axes = plt.subplots(ncols=2, figsize=(10,4), constrained_layout=True)
  while True:
    for ax in axes:
      ax.clear()

    if x_range is None or is_redo:
      _val = input('\nEnter x range of lower left plot to use for fit (min max): ')
      x_range = list( map(float, _val.split()) )
      log.write(f'x range = {x_range}')
    if y_range is None or is_redo:
      _val = input('Enter y range of lower left plot to use for fit (min max): ')
      y_range = list( map(float, _val.split()) )
      log.write(f'y range = {y_range}')

    mask_tafel = (x_tafel['GSA']>x_range[0]) & (x_tafel['GSA']<x_range[1]) & (y_tafel['GSA']>y_range[0]) & (y_tafel['GSA']<y_range[1])

    log.write('')
    m, b, rsq = [ dict() for _ in range(3) ]
    a = 0
    for const,rt in zip([gsa,ecsa],['GSA','ECSA']):
      fitresult, optvals = do_linear_fit(x_tafel[rt][mask_tafel], y_tafel[rt][mask_tafel])
      m[rt], b[rt] = optvals['m'], optvals['b']
      rsq[rt] = 1 - fitresult.residual.var() / np.var(y_tafel[rt][mask_tafel])

      # Plot Tafel slope
      axes[a].set(xlabel=f'log10(abs(I/{rt})', ylabel='Overpotential')
      axes[a].plot(x_tafel[rt][mask_tafel], y_tafel[rt][mask_tafel], c=colors[a])

      log.write(f'Tafel {rt} fit:  y = {m[rt]} * x  +  {b[rt]}')
      log.write(f'  r squared = {rsq[rt]}')


      output[f'I_Tafel_{rt}_LIN'] = x_tafel[rt][mask_tafel]
      output[f'E_Tafel_{rt}_LIN'] = y_tafel[rt][mask_tafel]

      a += 1

    plt.show(block=False)
    fig.canvas.draw()
    fig.canvas.flush_events()
    is_done = input('\nIs this good (y or n)? ')
    if is_done.lower()=='y':  # Exit loop
      plt.close('all')
      break
    else:
      is_redo = True

  return output



if __name__ == '__main__':
  """Run the full polarization curve analysis chain.
  To run:
    python polarization_curves.py config_pol.ini

  TODO:
    glob files
    data_folder = './'
    ecsa_fnames = glob.glob(f'{data_folder}/*_CV_*.txt')
    pol_fnames = glob.glob(f'{data_folder}/*_LSV_*.txt')
  """

  from ast import literal_eval
  from configparser import ConfigParser
  import glob
  import pandas as pd
  import sys

  from logger import Logger


  # Parse configuration (this automatically determines types)
  if len(sys.argv) < 2:
    print('You must enter a configuration file name. Please try again.')
    sys.exit(1)
  conf_file = ConfigParser()
  conf_file.read(sys.argv[1:])

  # Convert to dictionary format and implement correct data types
  conf = {k:literal_eval(v) for k,v in conf_file['DEFAULT'].items()}
  # print(conf)

  conf["data_folder"] += f'/sample {conf["sample"]}'

  # ECSA
  # Setup logging
  log_fname =  f'{conf["data_folder"]}/LOG_ECSA_{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}.txt'
  print(f'Log file name: {log_fname}')
  loggers = { 'ECSA': Logger(log_fname) }

  ecsa_fnames = [ f'{conf["data_folder"]}/{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}_her_{idx}_CV_C03.txt' for idx in conf["ecsa_scan_indices"] ]
  output_ecsa_fname = f'{conf["data_folder"]}/ECSA_{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}.csv'
  loggers['ECSA'].write('\nECSA file names:')
  for f in ecsa_fnames:
    loggers['ECSA'].write(f'  {f}')
  ecsa_val, ecsa_data = calculate_ecsa(loggers['ECSA'], ecsa_fnames, conf["ecsa_scan_rates"], conf["specific_capacitance"], blank_capacitance=conf["blank_capacitance"])
  loggers['ECSA'].write(f'ECSA value = {ecsa_val}')

  # Save ECSA file
  ecsa_data_df = pd.DataFrame.from_dict(ecsa_data, orient='index')
  ecsa_data_df = ecsa_data_df.transpose()
  ecsa_data_df.to_csv(output_ecsa_fname, index=False)
  loggers['ECSA'].write(f'Saving {output_ecsa_fname}')

  # Polarization curves
  for idx in conf["pol_scan_indices"]:
    pol_fname = f'{conf["data_folder"]}/{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}_her_{idx}_LSV_C03.txt'
    output_pol_fname = f'{conf["data_folder"]}/POL_{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}_{idx}.csv'
    log_fname = f'{conf["data_folder"]}/LOG_POL_{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}_{idx}.txt'
    loggers[f'POL{idx}'] = Logger(log_fname)
    pol_data = make_pol_curves(loggers[f'POL{idx}'], pol_fname, conf["ph"], conf["gsa"], ecsa_val, ru=conf["uncompensated_resistance"])

    # Save polarization curve file
    # for k,v in pol_data.items():
      # print(k, v.size)
    pol_data_df = pd.DataFrame.from_dict(pol_data, orient='index')
    pol_data_df = pol_data_df.transpose()
    pol_data_df.to_csv(output_pol_fname, index=False)
    loggers[f'POL{idx}'].write(f'\nSaving {output_pol_fname}')

  print('\nGreat success!\n')


