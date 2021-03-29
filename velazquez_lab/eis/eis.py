"""Produce IES curves."""

from ast import literal_eval
from configparser import ConfigParser
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate, optimize, linalg
import sys

from ecsa import colors
from logger import Logger


def circle(x, r, x0, y0):
  @np.vectorize
  def _func(_x):
    # return np.sqrt(r**2 - (x-x0)**2) + y0
    _val = r**2 - (_x-x0)**2
    if _val < 0:
      return -np.sqrt(np.abs(_val)) + y0
    return np.sqrt(_val) + y0
  return func(x)

# def circle_gradient(x, r, x0, y0):

def fit_semicircle(x,y):
  x_m = np.mean(x)
  y_m = np.mean(y)

  def calc_R(xc, yc):
    """Calculate the distance of each 2D points from the center (xc, yc) """
    return np.sqrt((x-xc)**2 + (y-yc)**2)

  def f_2(c):
    """Calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
    Ri = calc_R(*c)
    return Ri - Ri.mean()

  center_estimate = x_m, y_m
  center_2, ier = optimize.leastsq(f_2, center_estimate)

  xc_2, yc_2 = center_2
  Ri_2       = calc_R(xc_2, yc_2)
  R_2        = Ri_2.mean()
  residu_2   = sum((Ri_2 - R_2)**2)
  return R_2, xc_2, yc_2, residu_2


def find_cirlce_zeros(r, x0, y0):
  """Find where circle intersects x-axis.
  Notes:
    (x-x0)**2 + y0**2 - r**2 = 0, where y=0 (solve quadratic)
  """
  a = 1
  b = -2 * x0
  c = x0**2 + y0**2 - r**2

  d = (b**2) - (4*a*c)
  sol1 = (-b-np.sqrt(d))/(2*a)
  sol2 = (-b+np.sqrt(d))/(2*a)
  return np.array([sol1,sol2])


def eis(log, input_fnames, potentials):
  """Make EIS plot and find endpoints of circle."""
  output = {}

  # Setup plotting
  nplots = math.ceil(len(potentials)/4)
  fig1, axes1 = [ [] for _ in range(2) ]
  for i in range(nplots):
    f, ax = plt.subplots(nrows=2, ncols=2, figsize=(12,7), constrained_layout=True)
    fig1.append(f)
    for a in ax.flatten():
      axes1.append(a)

  for i,ax in enumerate(axes1):
    ax.set(xlabel='Re(Z)/Ohm', ylabel='-Im(Z)/Ohm')
    # ax.grid()
    if i>=nplots:
      a.axis('off')

  fig2, ax2 = plt.subplots(figsize=(6,4), constrained_layout=True)
  ax2.set(xlabel='Re(Z)/Ohm', ylabel='-Im(Z)/Ohm')
  # ax2.grid()

  # Loop over potential files
  bad_potentials = []
  for i,fname in enumerate(input_fnames):
    output[potentials[i]] = {}
    p = potentials[i]

    log.write(f'\nPotential: {potentials[i]}')

    # Load text file
    x, y = np.loadtxt(fname, delimiter='\t', unpack=True, skiprows=1)
    output[p]['x'], output[p]['y'] = x, y
    for ax in [ax2, axes1[i]]:
      ax.scatter(x, y, c=colors[i], marker='s', label=f'{p} V')

    # Determine if data file is good
    c_idx = np.argmax(y)
    if c_idx == y.size-1:  # If last point is the maximum then ignore
      log.write('Last point is the maximum, this file is now ignored.')
      bad_potentials.append(p)
      continue

    # Find range to fit (search for inflection points)
    f1 = np.gradient(y, x)  # 1st derivative
    f11 = np.gradient(f1, x)  # 2nd derivative
    # print(f'f11[c_idx] = {f11[c_idx]}')
    # print(f'f11 = {f11}')

    l_idx = c_idx - 1
    while True:
      if l_idx == 0:
        break
      # if True:  # Make sure slope is increasing by rate expected for circle
      if f11[l_idx]>0 and f11[l_idx-1]>0:  # Check for inflection point
        l_idx += 1
        break
      l_idx -= 1
    r_idx = c_idx + 1
    while True:
      if r_idx == y.size-1:
        break
      # if True:  # Make sure slope is increasing by rate expected for circle
      if f11[r_idx]>0 and f11[r_idx+1]>0:  # Check for inflection point
        r_idx -= 1
        break
      r_idx += 1

    axes1[i].axvline(x[l_idx], c='lightgray', linestyle=':', zorder=0)
    axes1[i].axvline(x[r_idx], c='lightgray', linestyle=':', zorder=0)

    # Fit semicircle and find zeros
    r, x0, y0, residual = fit_semicircle(x[l_idx:r_idx+1], y[l_idx:r_idx+1])  # Add 1 to include point at r_idx
    output[p]['r'], output[p]['x0'], output[p]['y0'] = np.array([r]), np.array([x0]), np.array([y0])
    # zeros = find_cirlce_zeros(r, x0, y0)
    # output[p]['zeros'] = zeros
    output[p]['fit_x'] = np.linspace(x0-r, x0+r, 100)
    output[p]['fit_y'] = circle(output[p]['fit_x'], r, x0, y0)
    for ax in [ax2, axes1[i]]:
      ax.plot(output[p]['fit_x'], output[p]['fit_y'], c=colors[i], linestyle='--')

    log.write(f'r = {r}\nx0 = {x0}\ny0 = {y0}')
    log.write(f'Residuals = {residual}')
    # log.write(f'Zeros found: {zeros}')
    log.write(f'Left edge:  x = {x0-r}')
    log.write(f'Right edge: x = {x0+r}')
    log.write(f'Diameter: {2*r}')

  # Draw plots
  for i in range(len(potentials)):
    axes1[i].legend(loc='upper right')
  ax2.legend(loc='upper right')
  plt.show(block=False)

  # User input to discard data sets
  print('\nDo you want to discard any data sets?')
  _good_pots = [ p for p in potentials if p not in bad_potentials ]
  bad_pots = input(f'Enter \'n\' or any of the potentials ({_good_pots}): ')
  if bad_pots != 'n':
    bad_pots = list(map(float,bad_pots.strip().split()))
    for p in bad_pots:
      bad_potentials.append(p)

  # Remove dictionary entries
  for p in bad_potentials:
    output.pop(p)

  return output



if __name__ == '__main__':
  """Run EIS analysis
  To run:
    python eis.py eis_config.ini
  """
  # Parse configuration (this automatically determines types)
  if len(sys.argv) < 2:
    print('You must enter a configuration file name. Please try again.')
    sys.exit(1)
  conf_file = ConfigParser()
  conf_file.read(sys.argv[1:])
  conf = {k:literal_eval(v) for k,v in conf_file['DEFAULT'].items()}

  # Setup logging
  log_fname =  f'{conf["data_folder"]}/LOG_EIS_{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}.txt'
  print(f'Log file name: {log_fname}')
  log = Logger(log_fname)

  # Determine file names
  eis_fnames = [ f'{conf["data_folder"]}/{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}_EIS_{idx}_PEIS_C01.txt' for idx in conf["eis_indices"] ]

  # Run macro
  eis_data = eis(log, eis_fnames, conf['potentials'])

  # Save data file
  log.write()
  for i,idx in enumerate(conf["eis_indices"]):
    p = conf['potentials'][i]
    if p not in eis_data:
      continue

    output_fname = f'{conf["data_folder"]}/EIS_{idx}_{conf["date"]}_{conf["compound"]}_sample{conf["sample"]}.csv'
    eis_data_df = pd.DataFrame.from_dict(eis_data[p], orient='index')
    eis_data_df = eis_data_df.transpose()
    eis_data_df.to_csv(output_fname, index=False)
    log.write(f'Saving {output_fname}')

  print('\nGreat success!\n')
