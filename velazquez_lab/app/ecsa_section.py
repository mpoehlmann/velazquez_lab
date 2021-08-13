"""Create user interface for ECSA section of polarization curve analysis.
See pol_page.py for usage.
"""

import dash
from dash.dash import no_update
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components import Keygen
import dash_table
import numpy as np
import os
import pandas as pd
import plotly.graph_objs as go

from velazquez_lab.app import templates
from velazquez_lab.pol import ecsa
from velazquez_lab.utils import styles
import velazquez_lab.utils.linear_fitting as ft


def build_ecsa_dlc_fig(file_storage, contour=None):
  """Specify a default scan rate."""
  for i, key in enumerate(file_storage.keys()):
    if file_storage[key]['scan_rate'] is None:
      file_storage[key]['scan_rate'] = f"File {i+1}"

  """Initialize figure."""
  dlc_fig = go.Figure()
  dlc_fig.update_layout(xaxis_title='<b>Potential (V)</b>', yaxis_title='<b>Current (mA)</b>', legend_title='<b>Scan rate (mV/s)</b>')

  """Add datasets."""
  if len(file_storage) > 0:
    for i, file in enumerate(file_storage.values()):
      trace = go.Scatter(x=file['potential'], y=file['current'], mode='lines', line_color=styles.colors[i], name=f"<b>{file['scan_rate']}</b>")
      dlc_fig.add_trace(trace)

  """Draw contour line."""
  dlc_fig.add_vline(
    x=contour, line_width=1, line_dash='dash', line_color='gray',
    annotation_text=' Potential contour', annotation_position='top right', annotation_font_size=12, annotation_font_color='gray',
  )

  return dlc_fig


def build_ecsa_fit_fig(fitres_df):
  fit_fig = go.Figure()
  fit_fig.update_layout(xaxis_title='<b>Scan rate (mV/s)</b>', yaxis_title='<b>Current (mA)</b>', showlegend=False)

  if len(fitres_df) == 0:
    return fit_fig

  for i, key in enumerate(('low', 'high')):
    fit_fig.add_trace( go.Scatter(x=fitres_df['scan_rate'], y=fitres_df[f'I_{key}'], mode='markers', marker=dict(color=styles.colors[i], size=12, symbol='square')) )

    x = fitres_df['scan_rate']
    y = ft.linear_eqn(fitres_df['scan_rate'], fitres_df.loc[0, f'slope_{key}'], fitres_df.loc[0, f'intercept_{key}'])
    fit_fig.add_trace( go.Scatter(x=x, y=y, mode='lines', line=dict(color=styles.colors[i], dash='dash')) )

    aloc = {'x': 0.02, 'y': 0.02} if key=='low' else {'x': 0.02, 'y': 0.98}
    fit_fig.add_annotation(
      x=aloc['x'], y=aloc['y'], xref='paper', yref='paper', showarrow=False, font=dict(size=14), align='left',
      text=f"<b>{key.capitalize()}er fit:</b><br>    m = {fitres_df.loc[0, f'slope_{key}']:.4g} F<br>    b = {fitres_df.loc[0, f'intercept_{key}']:.4g} mA<br>    r<sup>2</sup> = {fitres_df.loc[0, f'rsq_{key}']:.3f}",
    )

  return fit_fig


def build_ecsa_inputs(app):
  content = list()

  """File upload."""
  storage = dcc.Store(data=dict(), id='esca-file-storage', storage_type='memory')
  table = dash_table.DataTable(
    id='ecsa-file-table',
    columns=[
      {'name': 'File name', 'id': 'fname', 'type': 'text',},
      {'name': 'Scan rate (mV/s)', 'id': 'scan_rate', 'type': 'numeric',}
    ],
    data=[],
    style_table={'overflowX': 'scroll'},
    # style_cell={'whiteSpace': 'normal', 'height': 'auto'},
    # tooltip_duration=None,
    # style_cell={
    #     'overflow': 'hidden',
    #     'textOverflow': 'ellipsis',
    #     'maxWidth': 0,
    # },
    style_cell_conditional=[
      {'if': {'column_id': 'fname'}, 'width': '60%', 'textAlign': 'left'},
      {'if': {'column_id': 'scan_rate'}, 'width': '40%', 'textAlign': 'right'},
    ],
    editable=True,
    row_deletable=True,
  )
  file_uploader = dcc.Upload(
    id='ecsa-upload',
    className='file-uploader',
    children=html.Div(['Drag-and-drop or ', html.A('select files', className='btn-link'), ' to add']),
    multiple=True,
  )

  content.append(dbc.Container([
    # html.Div(load_cfg_btn, className='pb-1'),
    html.Div([storage, table]),
    html.Div(file_uploader, className='mt-1'),
  ]))
  content.append(html.Hr())

  """Input controls."""
  btn1 = dbc.InputGroup([
    dbc.InputGroupAddon('Potential contour', addon_type='prepend'),
    dbc.Input(id='ecsa-contour-input', value=0.175, type='number', step='any', placeholder='Potential contour (in V)'),
    dbc.InputGroupAddon('V', addon_type='append'),
  ])
  btn2 = dbc.InputGroup([
    dbc.InputGroupAddon('Specific capacitance', addon_type='prepend'),
    dbc.Input(id='ecsa-specific-input', value=1.0, type='number', step='any', placeholder='Specific capacitance'),
    dbc.InputGroupAddon('F/cm2', addon_type='append'),
  ])
  btn3 = dbc.InputGroup([
    dbc.InputGroupAddon('Black capacitance', addon_type='prepend'),
    dbc.Input(id='ecsa-blank-input', value=0.0, type='number', step='any', placeholder='Specific capacitance'),
    dbc.InputGroupAddon('F', addon_type='append'),
  ])
  btn_fit = dbc.Button('Fit', id='ecsa-fit-button', className='btn-block btn-primary', n_clicks=0)

  content.append(dbc.Container([
    html.Div(btn1, className='pb-1'),
    html.Div(btn2, className='pb-1'),
    html.Div(btn3, className='pb-1'),
    html.Div(btn_fit),
  ]))

  """Output display."""
  download = html.Div([
    dbc.Button('Download fit results', id='ecsa-download-button', className='btn-block btn-primary', n_clicks=0),
    dcc.Store(data={}, id='esca-fitresdf-storage', storage_type='memory'),
    dcc.Download(id='ecsa-download-dataframe-csv'),
  ])

  collapse_children = dbc.Container(
    dbc.Row(
      [
        dbc.Col(html.Div(id='ecsa-fit-value'), className='col-6'),
        dbc.Col(download, className='col-6'),
      ],
      className='align-items-center',
    ),
  )
  collapse = dbc.Collapse([html.Hr(), collapse_children], id='ecsa-fit-output', is_open=False)
  content.append(collapse)

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../docs/ecsa.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'ecsa', 'ECSA Instructions', dcc.Markdown(txt))
  layout = templates.build_card('Inputs', content, info=info)
  return layout


def build_ecsa_row(app):
  """Create content for ECSA row."""

  @app.callback(
    Output('ecsa-file-table', 'data'),
    # Output('ecsa-file-table', 'tooltip_data'),
    Output('esca-file-storage', 'data'),
    Output('esca-fitresdf-storage', 'data'),
    Output('ecsa-dlc-graph', 'figure'),
    Output('ecsa-fit-graph', 'figure'),
    Output('tafel-sa-input', 'value'),
    Output('tafel-satype-input', 'value'),
    Output('ecsa-fit-value', 'children'),
    Output('ecsa-fit-output', 'is_open'),
    Output('ecsa-download-dataframe-csv', 'data'),
    Input('ecsa-fit-button', 'n_clicks'),
    Input('ecsa-file-table', 'data'),
    Input('ecsa-upload', 'filename'),
    Input('ecsa-contour-input', 'value'),
    Input('ecsa-download-button', 'n_clicks'),
    State('ecsa-upload', 'contents'),
    State('esca-file-storage', 'data'),
    State('esca-fitresdf-storage', 'data'),
    State('ecsa-specific-input', 'value'),
    State('ecsa-blank-input', 'value'),
  )
  def ecsa_fit_callback(fit_btn_clicks, file_table, new_file_names, contour, download_nclicks, new_file_contents, file_storage, fitres_df, specific_cap, blank_cap): #, dlc_fig, fit_fig, ecsa_display_val):
    """Link ECSA elements together."""
    """Get id of component which triggered the callback."""
    ctx = dash.callback_context
    trig_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    """Convert file table to DataFrame."""
    fitres_df = pd.DataFrame.from_dict(fitres_df)
    file_table_df = pd.DataFrame.from_dict(file_table)

    ecsa_val, esca_val_text = no_update, no_update
    is_fitoutput_open = no_update
    download = None
    if trig_id == 'ecsa-upload':  # New file uploaded.
      if new_file_contents is not None:
        for n, c in zip(np.atleast_1d(new_file_names), np.atleast_1d(new_file_contents)):
          e, i = ecsa.load_data(templates.parse_file(c), cycle=2)
          file_storage[n] = {'scan_rate': None, 'potential': e[0], 'current': i[0]}
      is_fitoutput_open = False
      fitres_df = pd.DataFrame()

    elif trig_id == 'ecsa-file-table':  # Table data modified.
      pop_keys = []
      for key in file_storage:  # Iterate over DataFrame rows.
        if key not in file_table_df['fname'].values:  # Check if any rows have been deleted.
          # print(f"...removing {key}")
          pop_keys.append(key)
      for key in pop_keys:
        file_storage.pop(key)
      for row in file_table_df.itertuples():  # Check if scan rates have been modified.
        file_storage[row.fname]['scan_rate'] = row.scan_rate
      is_fitoutput_open = False
      fitres_df = pd.DataFrame()

    elif trig_id == 'ecsa-fit-button':  # Fit button clicked.
      if len(file_storage) == 0:
        raise FileNotFoundError("At least one file must be uploaded.")
      for i, file in enumerate(file_storage.values()):
        if file['scan_rate'] is None:
          raise ValueError("All scan rates must be defined.")

      e = [f['potential'] for f in file_storage.values()]  # TODO: convert to pandas
      i = [f['current'] for f in file_storage.values()]
      s = [f['scan_rate'] for f in file_storage.values()]
      ecsa_val, fitres_df = ecsa.calculate_ecsa(e, i, s, contour=contour, specific_cap=specific_cap, blank_cap=blank_cap)
      esca_val_text = f"ECSA = {ecsa_val:.4g} cm2"
      is_fitoutput_open = True

    elif trig_id == 'ecsa-download-button':
      download = dcc.send_data_frame(fitres_df.to_csv, 'ecsa_fit_results.csv', index=False)

    """Create return values."""
    outputs = tuple([
      [{'fname': key, 'scan_rate': val['scan_rate']} for key, val in file_storage.items()],
      file_storage,
      fitres_df.to_dict(orient='records'),
      build_ecsa_dlc_fig(file_storage, contour),
      build_ecsa_fit_fig(fitres_df),
      float(f"{ecsa_val:.5g}") if ecsa_val!=no_update else ecsa_val,
      'ECSA',
      esca_val_text,
      is_fitoutput_open,
      download,
    ])
    return outputs

  row = dbc.Row([
    dbc.Col(build_ecsa_inputs(app), className='col-3'),
    dbc.Col(templates.build_card('Double-layer capacitance', dcc.Graph(id='ecsa-dlc-graph')), className='col-4half',),
    dbc.Col(templates.build_card('Fit results', dcc.Graph(id='ecsa-fit-graph')), className='col-4half',),
  ])
  return row