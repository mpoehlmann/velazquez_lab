"""Calculate ECSA value."""

import lmfit
import matplotlib.pyplot as plt
import numpy as np

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


def do_linear_fit(x_vals, y_vals):
  """Fits data to linear model."""
  def eqn(x, m, b):
    return m*x + b
  myfit = lmfit.Model(eqn)
  pars = myfit.make_params()
  pars['m'].set(value=0, vary=True)
  pars['b'].set(value=0, vary=True)

  fitresult = myfit.fit(y_vals, pars, x=x_vals)
  optvals = fitresult.best_values

  return fitresult, optvals


def calculate_ecsa(log, input_fnames, scan_rates, cs, potential_contour=None, blank_capacitance=None):
  """Calculates ECSA from input data file.
  Args:
    input_fname (list(str)): list of input file names
    scan_rates (list(float)): dictionary of scan rates in mV/s corresponding to a scan index
    cs (float): specific capacitance
    potential_contour (float): potential at which to plot current vs. scan rate, if None then asks for manual user input
    blank_capacitance (float): if not None then subtracted from average slope
  Returns:
    float: ECSA in cm^2
  """
  output = dict()

  # Load text file
  potential, current, scan, idx = [ [] for _ in range(4) ]
  fig, axes = plt.subplots(ncols=2, figsize=(10,4), constrained_layout=True)
  axes[0].set(xlabel='Potential (V)', ylabel='Current (mA)')
  for idx,f in enumerate(input_fnames):
    e, i, s = np.loadtxt(f, delimiter='\t', unpack=True, skiprows=1)

    mask = (s==2)
    potential.append(e[mask])
    current.append(i[mask])
    scan.append(s[mask])

    # Plot current vs. potential of scan 2
    axes[0].plot(e[mask], i[mask], c=colors[idx])
    output[f'E_{idx}'] = e[mask]
    output[f'I_{idx}'] = i[mask]

  axes[1].axis('off')
  plt.show(block=False)

  # User input for potential
  if potential_contour is None:
    potential_contour = input('\nWhich potential do you want (in V)? ')
  new_p_contour = True

  bad_pts = np.array([])
  while True:
    if new_p_contour:
      # Find values on contour
      current_low, current_high , rate = [ [] for _ in range(3) ]
      for e, i, s in zip(potential, current, scan_rates):
        mid_idx = np.argmin(e)

        # Interpolate on line
        i1, i2 = [ np.interp(potential_contour, e[idx], i[idx]) for idx in [slice(0,mid_idx),slice(mid_idx,None)] ]
        current_low.append(min(i1,i2))
        current_high.append(max(i1,i2))
        rate.append(s)
      new_p_contour = False

    pt_mask = np.logical_not( np.isin(np.arange(len(rate)), bad_pts) )
    current_low = np.array(current_low)[pt_mask]
    current_high = np.array(current_high)[pt_mask]
    rate = np.array(rate)[pt_mask]

    # Plot current vs. scan rate
    axes[1].axis('on')
    axes[1].clear()
    axes[1].set(xlabel='Scan rate', ylabel='Current (mA)')
    axes[1].text(0.05, 0.95, f'Potential = {potential_contour} V', verticalalignment='top', horizontalalignment='left', transform=axes[1].transAxes)
    axes[1].scatter(rate, current_low, c=colors[0])
    axes[1].scatter(rate, current_high, c=colors[1])
    output['Scan Rate'] = rate
    output['I (low)'] = current_low
    output['I (high)'] = current_high

    log.write(f'Potential = {potential_contour} V')

    # Fit slopes and find averages
    fitresult_low, optvals_low = do_linear_fit(rate, current_low)
    m_low, b_low = optvals_low['m'], optvals_low['b']
    rsq_low = 1 - fitresult_low.residual.var() / np.var(current_low)

    fitresult_high, optvals_high = do_linear_fit(rate, current_high)
    m_high, b_high = optvals_high['m'], optvals_high['b']
    rsq_high = 1 - fitresult_high.residual.var() / np.var(current_high)

    x = 0.5 * (abs(m_low)+abs(m_high))
    log.write(f'\nLower slope: {m_low}')
    log.write(f'  r squared = {rsq_low}')
    log.write(f'Higher slope: {m_high}')
    log.write(f'  r squared = {rsq_high}')
    log.write(f'Average slope: {x}')


    # Optionally subtract blank capacitance
    if blank_capacitance is not None:
      x = x - blank_capacitance

    # Draw lines
    axes[1].plot(rate, m_low*np.asarray(rate) + b_low, c=colors[0])
    axes[1].plot(rate, m_high*np.asarray(rate) + b_high, c=colors[1])

    # Exit loop or repeat fit
    fig.canvas.draw()
    fig.canvas.flush_events()
    is_done = input('\nIs this good (y or n)? ')
    if is_done.lower()=='y':  # Exit loop
      plt.close('all')
      break

    # Choose action
    print('Do you want to:')
    print('  1. Keep this potential and throw away some points')
    print('  2. Choose a different potential')

    while True:
      action = int(input())

      if action==1:
        _pts = input(f'Which points would you like to discard (1-{rate.size} from left to right)? ')
        bad_pts = np.array(list(map(int,_pts.strip().split()))) - 1  # Minus 1 to get index
        log.write(f'Discarding points: {bad_pts}')
        break
      elif action==2:
        potential_contour = input('Which potential do you want (in V)? ')
        new_p_contour = True
        break
      else:
        print('Not a valid option. Try again.')

  return x/cs, output  # Divide by specific capacitance, divide by 1000000 to convert units

