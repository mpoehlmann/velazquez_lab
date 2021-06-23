"""Create user interface for ECSA section of polarization curve analysis.
See pol_page.py for usage.
"""

import dash
from dash.dash import no_update
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from io import StringIO
import numpy as np
import os
import pandas as pd
import plotly.graph_objs as go

from velazquez_lab.app import templates
from velazquez_lab.plot import styles
from velazquez_lab.pol import ecsa
from velazquez_lab.utils import fitting


def build_ecsa_dlc_fig(file_table_df, file_storage, contour=None):
  """Specify a default scan rate."""
  for i, row in enumerate(file_table_df.itertuples()):
    if row.scan_rate is None:
      file_table_df.loc[i, 'scan_rate'] = f"File {i+1}"

  """Initialize figures."""
  dlc_fig = go.Figure()
  dlc_fig.update_layout(xaxis_title='<b>Potential (V)</b>', yaxis_title='<b>Current (mA)</b>', legend_title='<b>Scan rate (units)</b>')

  """Add datasets."""
  files = [ StringIO(templates.parse_file(file_storage[fname])) for fname in file_table_df['fname'] ]
  if len(files) > 0:
    dfs = ecsa.load_data(files, file_table_df['scan_rate'])
    for i, (scan_rate, df) in enumerate(dfs.items()):
      trace = go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1], mode='lines', line_color=styles.colors[i], name=f"<b>{scan_rate}</b>")  # +markers
      dlc_fig.add_trace(trace)

  """Draw contour line."""
  dlc_fig.add_vline(
    x=contour, line_width=1, line_dash='dash', line_color='gray',
    annotation_text=' Potential contour', annotation_position='top right', annotation_font_size=12, annotation_font_color='gray',
  )

  return dlc_fig


def build_ecsa_fit_fig(fitres_df, fitres):
  fit_fig = go.Figure()
  fit_fig.update_layout(xaxis_title='<b>Scan rate (units)</b>', yaxis_title='<b>Current (mA)</b>', showlegend=False)

  if len(fitres_df)>0:
    x, y = fitres_df.iloc[:,0], fitres_df.iloc[:,1]
    fit_fig.add_trace( go.Scatter(x=x, y=y, mode='markers', marker=dict(color=styles.colors[0], size=12, symbol='square')) )

    x, y = fitres_df.iloc[:,0], fitres_df.iloc[:,2]
    fit_fig.add_trace( go.Scatter(x=x, y=y, mode='markers', marker=dict(color=styles.colors[1], size=12, symbol='square')) )

    x, y = fitres_df.iloc[:,0], fitting.linear_eqn(fitres_df.iloc[:,0], fitres['m_low'], fitres['b_low'])
    fit_fig.add_trace( go.Scatter(x=x, y=y, mode='lines', line=dict(color=styles.colors[0], dash='dash')) )

    x, y = fitres_df.iloc[:,0], fitting.linear_eqn(fitres_df.iloc[:,0], fitres['m_high'], fitres['b_high'])
    fit_fig.add_trace( go.Scatter(x=x, y=y, mode='lines', line=dict(color=styles.colors[1], dash='dash')) )

    fit_fig.add_annotation(
      x=0.02, y=0.02, xref='paper', yref='paper', showarrow=False, font=dict(size=14), align='left',
      text=f"<b>Lower fit:</b><br>    m = {fitres['m_low']:.4g} units<br>    r<sup>2</sup> = {fitres['rsq_low']:.3f}",
    )
    fit_fig.add_annotation(
      x=0.02, y=0.98, xref='paper', yref='paper', showarrow=False, font=dict(size=14), align='left',
      text=f"<b>Upper fit:</b><br>    m = {fitres['m_high']:.4g} units<br>    r<sup>2</sup> = {fitres['rsq_high']:.3f}",
    )

  return fit_fig


def build_ecsa_inputs(app):
  c = list()

  """File upload."""
  storage = dcc.Store(data=dict(), id='esca-file-storage', storage_type='memory')
  table = dash_table.DataTable(
    id='ecsa-file-table',
    columns=[
      {'name': 'File name', 'id': 'fname', 'type': 'text',},
      {'name': 'Scan rate (unit)', 'id': 'scan_rate', 'type': 'numeric',}
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

  c.append(dbc.Container([
    # dbc.Row(dbc.Col(load_cfg_btn), className='pb-1'),
    dbc.Row(dbc.Col([storage, table])),
    dbc.Row(dbc.Col(file_uploader), className='mt-1'),
  ]))
  c.append(html.Hr())

  """Input controls."""
  btn1 = dbc.InputGroup([
    dbc.InputGroupAddon('Potential contour', addon_type='prepend'),
    dbc.Input(id='ecsa-contour-input', value=0.175, type='number', step='any', placeholder='Potential contour (in V)'),
    dbc.InputGroupAddon('V', addon_type='append'),
  ])
  btn2 = dbc.InputGroup([
    dbc.InputGroupAddon('Specific capacitance', addon_type='prepend'),
    dbc.Input(id='ecsa-specific-input', value=1.0, type='number', step='any', placeholder='Specific capacitance'),
    dbc.InputGroupAddon('units', addon_type='append'),
  ])
  btn3 = dbc.InputGroup([
    dbc.InputGroupAddon('Black capacitance', addon_type='prepend'),
    dbc.Input(id='ecsa-blank-input', value=0.0, type='number', step='any', placeholder='Specific capacitance'),
    dbc.InputGroupAddon('units', addon_type='append'),
  ])
  btn_fit = dbc.Button('Fit', id='ecsa-fit-button', className='btn-block btn-primary', n_clicks=0)

  c.append(dbc.Container([
    dbc.Row(dbc.Col(btn1), className='pb-1'),
    dbc.Row(dbc.Col(btn2), className='pb-1'),
    dbc.Row(dbc.Col(btn3), className='pb-1'),
    dbc.Row(dbc.Col(btn_fit)),
  ]))

  """Output display."""
  download = html.Div([
    dbc.Button('Download fit results', id='ecsa-download-button', className='btn-block btn-primary', n_clicks=0),
    dcc.Store(data={}, id='esca-fitres-storage', storage_type='memory'),
    dcc.Store(data={}, id='esca-fitresdf-storage', storage_type='memory'),
    dcc.Download(id='ecsa-download-dataframe-csv'),
  ])

  collapse_children = dbc.Container(
    dbc.Row(
      [
        dbc.Col(
          html.Div(id='ecsa-fit-value'),
          className='col-6',
        ),
        dbc.Col(
          download,
          className='col-6',
        ),
      ],
      className='align-items-center',
    ),
  )
  collapse = dbc.Collapse([html.Hr(), collapse_children], id='ecsa-fit-output', is_open=False)
  c.append(collapse)


  @app.callback(
    Output('ecsa-file-table', 'data'),
    # Output('ecsa-file-table', 'tooltip_data'),
    Output('esca-file-storage', 'data'),
    Output('esca-fitres-storage', 'data'),
    Output('esca-fitresdf-storage', 'data'),
    Output('ecsa-dlc-graph', 'figure'),
    Output('ecsa-fit-graph', 'figure'),
    Output('pol-ecsa-input', 'value'),
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
    State('esca-fitres-storage', 'data'),
    State('esca-fitresdf-storage', 'data'),
    State('ecsa-specific-input', 'value'),
    State('ecsa-blank-input', 'value'),
  )
  def ecsa_fit_callback(fit_btn_clicks, file_table, new_file_names, contour, download_nclicks, new_file_contents, file_storage, fitres, fitres_df, specific_cap, blank_cap): #, dlc_fig, fit_fig, ecsa_display_val):
    """Link ECSA elements together."""
    """Get id of component which triggered the callback."""
    ctx = dash.callback_context
    trig_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    """Convert file table to DataFrame."""
    if len(file_table) == 0:
      file_table = {'fname': [], 'scan_rate': []}
    file_table_df = pd.DataFrame.from_dict(file_table)
    fitres_df = pd.DataFrame.from_dict(fitres_df)
    fitres = fitres

    ecsa_val, esca_val_text = no_update, no_update
    is_fitoutput_open = no_update
    download = None
    if trig_id == 'ecsa-upload':  # New file uploaded.
      if new_file_contents is not None:
        if isinstance(new_file_names, str):  # Make sure it's a list not a string
          new_file_names = [new_file_names]
          new_file_contents = [new_file_contents]
        for n, c in zip(new_file_names, new_file_contents):
          file_table_df = file_table_df.append({'fname': n, 'scan_rate': None}, ignore_index=True)  # Add files to table
          file_storage[n] = c
      is_fitoutput_open = False
      fitres_df = pd.DataFrame()
      fitres = {}

    elif trig_id == 'ecsa-file-table':  # Table data modified.
      pop_keys = []
      for key in file_storage:  # Iterate over DataFrame rows
        if key not in file_table_df['fname'].values:
          # print(f"...removing {key}")
          pop_keys.append(key)  # Remove stored file data if row is removed
      for key in pop_keys:
        file_storage.pop(key)
      is_fitoutput_open = False
      fitres_df = pd.DataFrame()
      fitres = {}

    elif trig_id == 'ecsa-fit-button':  # Fit button clicked.
      for i, row in enumerate(file_table_df.itertuples()):
        if row.scan_rate is None:
          raise ValueError("All scan rates must be defined.")

      files = [ StringIO(templates.parse_file(file_storage[fname])) for fname in file_table_df['fname'] ]
      if len(files) == 0:
        raise ValueError("At least one file must be uploaded.")  # FIXME: change type

      dfs = ecsa.load_data(files, file_table_df['scan_rate'])
      ecsa_val, fitres_df, fitres = ecsa.calculate_ecsa(dfs, contour, specific_cap, blank_cap)
      # print(fitres_df)
      esca_val_text = f"ECSA = {ecsa_val:.4g} units"
      is_fitoutput_open = True

    elif trig_id == 'ecsa-download-button':
      download = dcc.send_data_frame(fitres_df.to_csv, 'ecsa_fit_results.csv')

    """Create return values."""
    file_names = file_table_df.to_dict(orient='records')
    # file_names_tooltip = [
    #   {
    #     column: {'value': str(value), 'type': 'markdown'}
    #     for column, value in row.items()
    #   } for row in file_table_df.to_dict('records')
    # ]
    dlc_fig = build_ecsa_dlc_fig(file_table_df, file_storage, contour)
    fit_fig = build_ecsa_fit_fig(fitres_df, fitres)
    # return file_names, file_names_tooltip, file_storage, dlc_fig, fit_fig, no_update, is_fitoutput_open
    return file_names, file_storage, fitres, fitres_df.to_dict(orient='records'), dlc_fig, fit_fig, ecsa_val, esca_val_text, is_fitoutput_open, download

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../assets/docs/ecsa.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'ecsa', 'ECSA Instructions', dcc.Markdown(txt))
  content = c  # dbc.Container([dbc.Row(_c) for _c in c], fluid=True)
  layout = templates.build_card('ECSA: Inputs', content, info=info)
  return layout


