"""Create user interface for polarization curve analysis.
See app.py for usage.
"""

import dash
from dash.dash import no_update
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from io import StringIO
import numpy as np
import os
import pandas as pd
import plotly.graph_objs as go

from velazquez_lab.app import templates
from velazquez_lab.plot import styles
from velazquez_lab.utils import filtering


def create_filt_fig(raw=None, filt=None):
  fig = go.Figure()
  fig.update_layout(xaxis_title='<b>Samples</b>', yaxis_title='<b>Title Goes Here</b>')

  if raw is not None:
    tr = go.Scatter(y=raw, mode='lines', line_color=styles.colors[0], name=f"<b>Raw</b>")
    fig.add_trace(tr)
  if filt is not None:
    tr = go.Scatter(y=filt, mode='lines', line_color=styles.colors[1], name=f"<b>Filtered</b>")
    fig.add_trace(tr)
  return fig


def create_filt_page(app):
  file_storage = dcc.Store(data=dict(), id='filt-file-storage', storage_type='memory')
  file_uploader = dcc.Upload(
    id='filt-upload',
    className='file-uploader',
    children=html.Div(['Drag-and-drop or ', html.A('select file', className='btn-link')]),
    multiple=False,
  )
  output_storage = dcc.Store(data=dict(), id='filt-output-storage', storage_type='memory')
  btn1 = dbc.InputGroup([
    dbc.InputGroupAddon('Window length', addon_type='prepend'),
    dbc.Input(id='filt-window-btn', type='number', min=7, max=101, step=2, value=51),  # Must be odd and greater than polyorder=5
    dbc.InputGroupAddon('samples', addon_type='append'),
  ])
  collapse = dbc.Collapse(
    dbc.Alert('The window length must be odd and greater than the filter polynomial order (5).', className='alert-warning'),
    id='filt-window-error',
    is_open=False
  )
  btn2 = dbc.Button('Optimize window length', n_clicks=0, id='filt-optimize-btn', className='btn-block btn-primary mr-1')

  @app.callback(
    Output('filt-file-name', 'children'),
    Output('filt-file-storage', 'data'),
    Output('filt-output-storage', 'data'),
    Output('filt-graph', 'figure'),
    Output('filt-window-btn', 'max'),
    Output('filt-window-error', 'is_open'),
    Input('filt-upload', 'filename'),
    Input('filt-window-btn', 'value'),
    Input('filt-optimize-btn', 'n_clicks'),
    State('filt-upload', 'contents'),
    State('filt-file-storage', 'data'),
  )
  def filt_callback(new_file_name, window_length, _, new_file_content, file_df):
    """Link filtering elements together."""
    """Get id of component which triggered the callback."""
    ctx = dash.callback_context
    trig_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    file_name, output_storage = (no_update for _ in range(2))
    file_df = pd.DataFrame.from_dict(file_df)
    window_max = no_update
    show_error = False

    if trig_id == 'filt-upload':
      if new_file_content is not None:
        file_name = new_file_name
        f = StringIO(templates.parse_file(new_file_content))
        file_df = pd.read_table(f, sep=',', header=None)
        window_max = len(file_df)
        if window_max%2 == 0:
          window_max -= 1

    if window_length is None:
      window_length = 0
    if len(file_df) > 0:
      if window_length<=5 or window_length%2==0:
        show_error = True
        fig = create_filt_fig(file_df.iloc[:,1], None)
      else:
        if trig_id == 'filt-optimize-btn':
          window_length, filt_y = filtering.optimize_window(file_df.iloc[:,1], polyorder=5)
        else:
          filt_y = filtering.apply_filter(file_df.iloc[:,1], window_length=window_length, polyorder=5)
        output_storage = filt_y
        fig = create_filt_fig(file_df.iloc[:,1], filt_y)
    else:
      fig = create_filt_fig(None, None)
    return file_name, file_df.to_dict(orient='records'), output_storage, fig, window_max, show_error

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../docs/filtering.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'filt', 'Filtering Instructions', dcc.Markdown(txt))
  inputs = templates.build_card(
    'Inputs',
    dbc.Container([
      dbc.Row(dbc.Col(file_uploader), className='pb-1'),
      dbc.Row(dbc.Col(id='filt-file-name'), className='pb-1'),
      dbc.Row(dbc.Col(btn1), className='pb-1'),
      dbc.Row(dbc.Col(collapse), className='pb-1'),
      dbc.Row(dbc.Col(btn2), className='pb-1'),
      file_storage,
      output_storage,
    ]),
    info=info
  )

  row = [
    dbc.Col(inputs, className='col-4'),
    dbc.Col(templates.build_card('Graph', dcc.Graph(id='filt-graph')), className='col-8'),
  ]

  pg = templates.build_page(sections={'Filtering': row})
  return pg