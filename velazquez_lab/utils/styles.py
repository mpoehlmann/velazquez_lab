"""
Plotting styles for the Velazquez Lab.
"""
from cycler import cycler
import matplotlib as mpl
import matplotlib.colors as mcol
import plotly.graph_objects as go
import plotly.io as pio


# COLORS = ['#9D7FC1', '#5589BA', '#60A6A7']
# COLORS = ['#9D7FC1', '#5589BA', '#60A6A7', '#4363d8', '#f58231', '#3cb44b', '#e6194B', '#911eb4', '#800000', '#000075', '#f032e6', '#42d4f4', '#bfef45', '#ffe119', '#a9a9a9', '#000000']
COLORS = ['#4363d8', '#f58231', '#3cb44b', '#e6194B', '#911eb4', '#800000', '#000075', '#f032e6', '#42d4f4', '#bfef45', '#ffe119', '#a9a9a9', '#000000']


def get_axes_ranges(x, y, x_padding=0, y_padding=0.05):
  """Determine axis bounds with fractional padding on either side.
  Args:
    x (array_like): x values.
    y (array_like): y values.
    x_padding (float): Fractional padding on x-axis.
    y_padding (float): Fractional padding on y-axis.
  Returns:
    x_range (list): x-axis range.
    y_range (list): y-axis range.
  """
  xmin = min(x)
  xmax = max(x)
  xax_min = xmin - x_padding * (xmax - xmin)
  xax_max = xmax + x_padding * (xmax - xmin)

  ymin = min(y)
  ymax = max(y)
  yax_min = ymin - y_padding * (ymax - ymin)
  yax_max = ymax + y_padding * (ymax - ymin)
  return [xax_min, xax_max], [yax_min, yax_max]


def color_to_rgba(color, alpha=1, lib='plotly'):
  """Convert either hex or named color to RGBA.
  Args:
    color (str): Hex or named color.
    alpha (float): Opacity for the color.
  """
  # if color[0] == '#':  # Hex string
    # rgb = pcol.hex_to_rgb(color)
  # else:
  rgb = mcol.to_rgba(color)[:3]
  if lib == 'plotly':
    return f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha})"
  elif lib == 'mpl':
    return tuple([rgb[0], rgb[1], rgb[2], alpha])
  else:
    raise ValueError(f"Plotting library not yet implemented: {lib}")


def set_plotly_style(theme='light'):
  """Setup plotly figure style.
  Args:
    theme (str): Theme name
      Currently 'light' is implemented.
  """
  ax_props = dict(
    showline=True, mirror=True, linewidth=2, showgrid=False, zeroline=False,
    ticks='outside', tickwidth=2, tickprefix="<b>",ticksuffix ="</b>",
    automargin=True,
  )
  layout = go.Layout(
    # width=600, height=450, autosize=False,
    autosize=True,
    margin={'l': 5, 'r': 5, 'b': 5, 't': 30, 'pad': 0},
    font=dict(family='Arial', size=18),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    modebar_remove=['select', 'autoScale', 'toggleSpikelines', 'toggleHover', 'lasso2d'],
  )

  if theme == 'light':
    ax_props['linecolor'] = 'black'
    layout['xaxis'] = ax_props
    layout['yaxis'] = ax_props
    layout['font']['color'] = 'black'
    layout['colorway'] = COLORS

    pio.templates["jessica_light"] = go.layout.Template(layout=layout)
    pio.templates.default = "plotly_white+jessica_light"

  elif theme == 'dark':
    ax_props['linecolor'] = 'white'
    layout['xaxis'] = ax_props
    layout['yaxis'] = ax_props
    layout['font']['color'] = 'white'
    layout['colorway'] = COLORS

    pio.templates["jessica_dark"] = go.layout.Template(layout=layout)
    pio.templates.default = "plotly_dark+jessica_dark"

  else:
    raise ValueError(f"Theme {theme} not yet implemented.")


def set_matplotlib_style():
  """Set matplotlib style.
  Notes:
    See https://matplotlib.org/tutorials/introductory/customizing.html.
  """
  mpl.rcParams['font.size'] = 16
  mpl.rcParams['font.family'] = 'Arial'
  mpl.rcParams['font.weight'] = 700

  mpl.rcParams['axes.titlesize'] = 18
  mpl.rcParams['axes.labelsize'] = 18  # 14
  mpl.rcParams['xtick.labelsize'] = 16  # 12
  mpl.rcParams['ytick.labelsize'] = 16  # 12

  mpl.rcParams['axes.titleweight'] = 'bold'
  mpl.rcParams['axes.labelweight'] = 'bold'
  mpl.rcParams['axes.linewidth'] = 2

  mpl.rcParams['xtick.bottom'] = True
  mpl.rcParams['ytick.left'] = True

  mpl.rcParams['xtick.direction'] = 'in'
  mpl.rcParams['xtick.minor.visible'] = True
  mpl.rcParams['xtick.major.size'] = 7
  mpl.rcParams['xtick.major.width'] = 2
  mpl.rcParams['xtick.minor.width'] = 2
  mpl.rcParams['xtick.minor.size'] = 3.5

  mpl.rcParams['ytick.direction'] = 'in'
  mpl.rcParams['ytick.minor.visible'] = True
  mpl.rcParams['ytick.major.size'] = 7
  mpl.rcParams['ytick.major.width'] = 2
  mpl.rcParams['ytick.minor.width'] = 2
  mpl.rcParams['ytick.minor.size'] = 3.5

  mpl.rcParams['legend.fontsize'] = 'small'
  mpl.rcParams['axes.grid'] = False
  mpl.rcParams['grid.alpha'] = 0.7
  mpl.rcParams['grid.linestyle'] = '--'
  mpl.rcParams['grid.linewidth'] = 0.6

  mpl.rcParams['figure.constrained_layout.use'] = True
  mpl.rcParams['figure.constrained_layout.hspace'] = 0.04
  mpl.rcParams['figure.constrained_layout.wspace'] = 0.04

  mpl.rcParams['figure.figsize'] = 6.5, 4.5
  mpl.rcParams['figure.dpi'] = 100
  mpl.rcParams['savefig.dpi'] = 500  # 1200

  mpl.rcParams['mathtext.default'] = 'regular'

  mpl.rcParams['axes.prop_cycle'] = cycler('color', COLORS)
  mpl.rcParams['image.cmap'] = 'inferno'