"""
Create user interface for Tafel slope section of polarization curve analysis.
Notes:
  See pol_page.py for usage.
"""

import dash
from dash.dash import no_update, PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from io import StringIO
from dash_html_components.Content import Content
import numpy as np
import os
import pandas as pd
import plotly.graph_objs as go

from velazquez_lab.app import templates
from velazquez_lab.pol import tafel_slope
from velazquez_lab.utils import styles


def build_tafel_figs(file_df, result_storage, sa_val, sa_type, log_i_range=None, e_range=None):
  """Initialize figures."""
  fig_raw, fig_pol, fig_tafel = ( go.Figure() for _ in range(3) )
  fig_raw.update_layout(xaxis_title='<b>E<sub>WE</sub> (V vs Ag/AgCl)</b>', yaxis_title='<b>I (mA)</b>', showlegend=True)
  fig_pol.update_layout(xaxis_title='<b>E<sub>WE</sub> (V vs RHE)</b>', yaxis_title=f'<b><i>j</i> (mA/cm<sup>2</sup><sub>{sa_type}</sub>)</b>', showlegend=True)
  fig_tafel.update_layout(xaxis_title=f'<b>log<sub>10</sub>(mA/cm<sup>2</sup><sub>{sa_type}</sub>)</b>', yaxis_title='<b>E<sub>WE</sub> (V vs RHE)</b>', showlegend=True)

  if len(file_df) > 0:
    """Raw polarization curve."""
    trace = go.Scatter(x=file_df['E'], y=file_df['I'], mode='lines', line_color=styles.colors[0], name='Data')
    fig_raw.add_trace(trace)

    """Corrected polarization curve."""
    trace = go.Scatter(x=file_df['E_rhe'], y=file_df['I_sa'], mode='lines', line_color=styles.colors[0], name='Data')
    fig_pol.add_trace(trace)

    """Tafel slope."""
    trace = go.Scatter(x=file_df['log10_I_sa'], y=file_df['E_rhe'], mode='lines', line_color=styles.colors[0], name='Data')
    fig_tafel.add_trace(trace)

    """Draw fit region."""
    box_args = dict(fillcolor='rgba(220,220,220,0.5)', line=dict(color='rgba(0,0,0,0)'))
    x_range, y_range = styles.get_axes_ranges(file_df['log10_I_sa'], y=file_df['E_rhe'])
    fig_tafel.update_xaxes(range=x_range)
    fig_tafel.update_yaxes(range=y_range)
    if log_i_range is not None:
      fig_tafel.add_vrect(x0=x_range[0], x1=log_i_range[0], **box_args)
      fig_tafel.add_vrect(x0=log_i_range[1], x1=x_range[1], **box_args)
    if e_range is not None:
      fig_tafel.add_hrect(y0=y_range[0], y1=e_range[0], **box_args)
      fig_tafel.add_hrect(y0=e_range[1], y1=y_range[1], **box_args)

  if len(result_storage)>0:
    trace = go.Scatter(x=result_storage['log_i'], y=result_storage['e'], mode='lines', line=dict(color=styles.colors[1], dash='dash'), name='Fit')
    fig_tafel.add_trace(trace)

  return fig_raw, fig_pol, fig_tafel


def build_tafel_inputs(app):
  """Create inputs."""
  content = list()

  """Data loading and normalization inputs."""
  file_uploader = dcc.Upload(
    id='tafel-upload',
    className='file-uploader',
    children=html.Div(['Drag-and-drop or ', html.A('select file', className='btn-link')]),
    multiple=False,
  )
  file_display = html.Div(id='tafel-file-display')
  storage = dcc.Store(data=dict(), id='tafel-file-storage', storage_type='memory')

  btn1 = dbc.InputGroup([
    dbc.InputGroupAddon('Surface area', addon_type='prepend'),
    dbc.Input(id='tafel-sa-input', value=1, type='number', required=True, step='any', placeholder='ECSA value'),
    dbc.InputGroupAddon('cm2', addon_type='append'),
  ])
  btn2 = dbc.InputGroup([
    dbc.InputGroupAddon("Surface area type", addon_type="prepend"),
    dbc.Select(
      id='tafel-satype-input',
      options=[
        {'label': 'Electrochemical', 'value': 'ECSA'},
        {'label': 'Geometric', 'value': 'GSA'},
      ],
      value='ECSA',
      required=True,
      placeholder='Select surface area type',
    ),
  ])
  btn3 = dbc.InputGroup([
    dbc.InputGroupAddon('pH', addon_type='prepend'),
    dbc.Input(id='tafel-ph-input', value=3, type='number', required=True, step='any', placeholder='pH level'),
  ])
  btn4 = dbc.InputGroup([
    dbc.InputGroupAddon('Ru', addon_type='prepend'),
    dbc.Input(id='tafel-ru-input', value=0, type='number', required=True, step='any', placeholder='Uncompensated resistance value'),
    dbc.InputGroupAddon('UNITS', addon_type='append'),
  ])
  content.append(dbc.Container([
    html.Div([file_uploader, file_display, storage], className='pb-1'),
    html.Div(btn1, className='pb-1'),
    html.Div(btn2, className='pb-1'),
    html.Div(btn3, className='pb-1'),
    html.Div(btn4, className=''),
  ]))

  content.append(html.Hr())

  """Tafel inputs."""
  btn1 = dbc.InputGroup(
    [
      dbc.InputGroupAddon('x range', addon_type='prepend'),
      dbc.Input(id='tafel-logimin-input', value=0, type='number', required=True, step='any', placeholder='Ewe min'),
      dbc.Input(id='tafel-logimax-input', value=1, type='number', required=True, step='any', placeholder='Ewe max'),
      dbc.InputGroupAddon('UNITS', addon_type='append'),
    ],
  )
  btn2 = dbc.InputGroup(
    [
      dbc.InputGroupAddon('y range:', addon_type='prepend'),
      dbc.Input(id='tafel-emin-input', value=0, type='number', required=True, step='any', placeholder='Ewe min'),
      dbc.Input(id='tafel-emax-input', value=1, type='number', required=True, step='any', placeholder='Ewe max'),
      dbc.InputGroupAddon('V', addon_type='append'),
    ],
  )
  btn3 = dbc.InputGroup(
    [
      dbc.InputGroupAddon("Fit model", addon_type="prepend"),
      dbc.Select(
        id='tafel-model-input',
        options=[
          {'label': 'CO2 reduction', 'value': 'co2'},
          {'label': 'Hydrogen evolution reaction (HER)', 'value': 'her'},
        ],
        value='co2',
        required=True,
        placeholder='Select fit model',
      ),
    ]
  )
  btn4 = dbc.InputGroup(
    [
      dbc.InputGroupAddon("Fit method", addon_type="prepend"),
      dbc.Select(
        id='tafel-fitmethod-input',
        options=[
          {'label': 'Least squares', 'value': 'lsq'},
          {'label': 'Bayesian (julius)', 'value': 'bayesian'},
        ],
        value='lsq',
        required=True,
        placeholder='Select fit method',
      ),
    ]
  )
  btn_run = dbc.Button('Calculate Tafel slope', className='btn-block btn-primary', id='tafel-run-btn', n_clicks=0)
  content.append(dbc.Container([
    html.Div(btn1, className='pb-1'),
    html.Div(btn2, className='pb-1'),
    html.Div(btn3, className='pb-1'),
    html.Div(btn4, className='pb-1'),
    html.Div(btn_run, className=''),
  ]))

  """Fit output display."""
  storage = dcc.Store(data=dict(), id='tafel-result-storage', storage_type='memory')
  download = html.Div([
    dbc.Button('Download fit results', id='tafel-download-button', className='btn-block btn-primary', n_clicks=0),
    dcc.Download(id='tafel-download-dataframe-csv'),
    storage,
  ])

  collapse_children = dbc.Container([
    html.Div(id='tafel-slope-val'),
    download,
  ])
  collapse = dbc.Collapse([html.Hr(), collapse_children], id='tafel-fit-output', is_open=False)
  content.append(collapse)

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../docs/tafel.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'tafel', 'Polarization Curve & Tafel Slope Instructions', dcc.Markdown(txt))
  layout = templates.build_card('Inputs', content, info=info)
  return layout


def build_tafel_row(app):
  """Create content for Tafel slope row."""

  @app.callback(
    Output('tafel-file-display', 'children'),
    Output('tafel-file-storage', 'data'),
    Output('tafel-emin-input', 'value'),
    Output('tafel-emax-input', 'value'),
    Output('tafel-logimin-input', 'value'),
    Output('tafel-logimax-input', 'value'),
    Output('pol-raw-graph', 'figure'),
    Output('pol-corr-graph', 'figure'),
    Output('tafel-graph', 'figure'),
    Output('tafel-result-storage', 'data'),
    Output('tafel-slope-val', 'children'),
    Output('tafel-fit-output', 'is_open'),
    Output('tafel-download-dataframe-csv', 'data'),
    Input('tafel-upload', 'filename'),
    Input('tafel-run-btn', 'n_clicks'),
    Input('tafel-sa-input', 'value'),
    Input('tafel-satype-input', 'value'),
    Input('tafel-ph-input', 'value'),
    Input('tafel-ru-input', 'value'),
    Input('tafel-emin-input', 'value'),
    Input('tafel-emax-input', 'value'),
    Input('tafel-logimin-input', 'value'),
    Input('tafel-logimax-input', 'value'),
    State('tafel-fitmethod-input', 'value'),
    State('tafel-model-input', 'value'),
    State('tafel-upload', 'contents'),
    State('tafel-file-storage', 'data'),
    State('tafel-result-storage', 'data'),
  )
  def tafel_fit_callback(new_file_name, run_btn_clicks, sa_val, sa_type, ph, ru, e_min, e_max, log_i_min, log_i_max, fitmethod, model, new_file_content, file_storage, result_storage):
    """Link Tafel slope elements together."""
    ctx = dash.callback_context
    trig_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    """Get values from storage"""
    file_df = pd.DataFrame.from_dict(file_storage)
    file_name = no_update
    tafel_slope_val = no_update
    is_fitoutput_open = False
    download = None

    if trig_id == 'tafel-upload':  # New file uploaded.
      file_df = tafel_slope.load_data(templates.parse_file(new_file_content))
      file_df= file_df[file_df['I'] != 0]  # Remove zeros.
      for c in ['E_rhe', 'I_sa', 'log10_I_sa']:
        file_df.insert(len(file_df.columns), c, np.full(len(file_df), np.nan))
      file_name = new_file_name

    if len(file_df) > 0:
      file_df['E_rhe'] = tafel_slope.correct_potential(file_df['E'], file_df['I'], ph, ru)
      file_df['I_sa'] = file_df['I'] / sa_val
      file_df['log10_I_sa'] = np.log10(np.abs(file_df['I_sa']))

      if trig_id in ['tafel-upload', 'tafel-sa-input', 'tafel-ph-input', 'tafel-ru-input']:
        e_min = float(f"{file_df['E_rhe'].min():.4g}")
        e_max = float(f"{file_df['E_rhe'].max():.4g}")
        log_i_min = float(f"{file_df['log10_I_sa'].min():.4g}")
        log_i_max = float(f"{file_df['log10_I_sa'].max():.4g}")

    if trig_id == 'tafel-run-btn':
      e, log_i = file_df['E_rhe'].to_numpy(), file_df['log10_I_sa'].to_numpy()
      mask = (e>=e_min) & (e<=e_max) & (log_i>=log_i_min) & (log_i<=log_i_max)
      e, log_i = e[mask], log_i[mask]
      if fitmethod == 'lsq':
        tafel_slope_val, result_storage['rsq'], result_storage['e'], result_storage['log_i'] = tafel_slope.fit_tafel_slope_lsq(e, log_i, model=model)
      # elif fitmethod == 'bayesian':
        # tafel_slope_val, rsq, res_voltages, res_log_currents = tafel_slope.fit_tafel_slope_bayesian(e, log_i, model=model)
      else:
        raise ValueError(f"Fit method '{fitmethod}' not implemented.")
      is_fitoutput_open = True

    if trig_id == 'tafel-download-button':
      pass
      # FIXME
      # download = dcc.send_data_frame(fitres_df.to_csv, 'tafel_fit_results.csv')

    """Prepare return values."""
    fig_raw, fig_corr, fig_tafel = build_tafel_figs(file_df, result_storage, sa_val, sa_type, log_i_range=[log_i_min, log_i_max], e_range=[e_min, e_max])
    outputs = tuple([
      file_name,
      file_df.to_dict(orient='records'),
      e_min, e_max, log_i_min, log_i_max,
      fig_raw,
      fig_corr,
      fig_tafel,
      result_storage,
      float(f"{tafel_slope_val:.4g} mV/decade") if tafel_slope_val!=no_update else no_update,
      is_fitoutput_open,
      download,
    ])
    return outputs

  tafel_row = dbc.Row(
    [
      dbc.Col(build_tafel_inputs(app), className='col-3'),
      dbc.Col(
        [
          dbc.Row(dbc.Col(templates.build_card('Raw polarization curve', dcc.Graph(id='pol-raw-graph')))),
          html.Br(),
          dbc.Row(dbc.Col(templates.build_card('Tafel slope', dcc.Graph(id='tafel-graph')))),
        ],
        className='col-4half',
      ),
      dbc.Col(
        [
          templates.build_card('Corrected polarization curve', dcc.Graph(id='pol-corr-graph')),
        ],
        className='col-4half',
      ),
    ]
  )
  return tafel_row