"""Create Velazquez Lab logo."""

import matplotlib.pyplot as plt
from matplotlib import patches


def create_logo():
  fig, ax = plt.subplots(figsize=(4,4))
  ax.set_frame_on(False)
  ax.get_yaxis().set_visible(False)
  ax.get_xaxis().set_visible(False)
  ax.set_xlim(-0.5, 0.5)
  ax.set_ylim(-0.5, 0.5)

  p = patches.RegularPolygon((0,0), 6, radius=1)
  ax.add_patch(p)


if __name__ == '__main__':
  """Create Velazquez Lab logo."""
  create_logo()