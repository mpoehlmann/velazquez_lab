"""
Plotting styles for the Velazquez Lab.
"""

import matplotlib.colors as mcol
import plotly.graph_objects as go
import plotly.io as pio


colors = ['#4363d8', '#f58231', '#3cb44b', '#e6194B', '#911eb4', '#800000', '#000075', '#f032e6', '#42d4f4', '#bfef45', '#ffe119', '#a9a9a9', '#000000']


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
    layout['colorway'] = colors

    pio.templates["jessica_light"] = go.layout.Template(layout=layout)
    pio.templates.default = "plotly_white+jessica_light"

  elif theme == 'dark':
    ax_props['linecolor'] = 'white'
    layout['xaxis'] = ax_props
    layout['yaxis'] = ax_props
    layout['font']['color'] = 'white'
    layout['colorway'] = colors

    pio.templates["jessica_dark"] = go.layout.Template(layout=layout)
    pio.templates.default = "plotly_dark+jessica_dark"

  else:
    raise ValueError(f"Theme {theme} not yet implemented.")


def color_to_rgba(color, alpha=1):
  """Convert either hex or named color to RGBA.
  Args:
    color (str): Hex or named color.
    alpha (float): Opacity for the color.
  """
  # if color[0] == '#':  # Hex string
    # rgb = pcol.hex_to_rgb(color)
  # else:
  rgb = mcol.to_rgba(color)[:3]
  return f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha})"


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