"""TODO."""

import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.special import factorial


def apply_filter(raw, window_length, polyorder, **kwargs):
  """TODO."""
  return savgol_filter(raw, window_length, polyorder, **kwargs)


def optimize_window(raw, polyorder=5, **kwargs):
  """Optimize Savitzky-Golay filter window length."""
  """Use analytic formula for window_length.
  https://arxiv.org/pdf/1808.10489.pdf
  """
  n = polyorder + 2
  pts = copy.deepcopy(raw)
  while True:  # n+2 derivative
    if n==0:
      break
    pts = np.gradient(pts)
    n -= 1
  vn = np.sum(pts**2) / raw.size
  val = (2 * (polyorder+2) * factorial(2*polyorder+3)**2 * np.std(raw)**2) / (factorial(polyorder+1)**2 * vn)
  window_length = val ** (1/(2*polyorder+5))
  window_length = int(window_length)
  if window_length%2 == 0:  # Make sure it's odd
    window_length += 1
  print(vn, val, window_length)
  return window_length, apply_filter(raw, window_length, polyorder)


if __name__ == '__main__':
  df = pd.read_csv('../../data/example_filter.csv', header=None)
  window_length, filt = optimize_window(df.iloc[:,1], 5)

  fig, ax = plt.subplots()
  ax.plot(df[0], df[1], label='Raw')
  ax.plot(df[0], filt, label='Filtered')
  ax.legend()
  plt.show()