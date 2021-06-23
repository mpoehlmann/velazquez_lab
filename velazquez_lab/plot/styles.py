"""Plotting styles for the Velazquez Lab."""

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
