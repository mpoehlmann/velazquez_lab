"""
Write script to find optimal window.
  sum of abs distances from filt to raw
"""

import copy
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.special import factorial


def apply_filter(y, window_length=None, polyorder=5, **kwargs):
  """TODO."""
  if window_length is None:
    """Use analytic formula for window_length.
    https://arxiv.org/pdf/1808.10489.pdf
    """
    n = polyorder + 2
    pts = copy.deepcopy(y)
    while True:  # n+2 derivative
      if n==0:
        break
      pts = np.gradient(pts)
      n -= 1
    vn = np.sum(pts**2) / y.size
    val = (2 * (polyorder+2) * factorial(2*polyorder+3)**2 * np.std(y)**2) / (factorial(polyorder+1)**2 * vn)
    window_length = val ** (2*polyorder+5)
  return savgol_filter(y, window_length, polyorder, **kwargs)


if __name__ == '__main__':
  import matplotlib.pyplot as plt

  df = pd.read_csv('../../data/example_filter.csv', header=None)
  window_length = None
  # window_length = int(0.005 * df[0].size)
  # if window_length%2 == 0:  # Must be odd
  #   window_length += 1
  filt = apply_filter(df, window_length)


  fig, ax = plt.subplots()
  ax.plot(df[0], df[1], label='Raw')
  ax.plot(df[0], filt, label='Filtered')
  ax.legend()
  plt.show()