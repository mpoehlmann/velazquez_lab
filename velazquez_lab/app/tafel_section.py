"""Create user interface for Tafel slope section of polarization curve analysis.
See pol_page.py for usage.
"""

import dash
from dash.dash import no_update, PreventUpdate
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
from velazquez_lab.pol import tafel_slope
from velazquez_lab.plot import styles


def build_tafel_figs(file_df, result_df, ecsa_val, gsa_val, fit_xmin, fit_xmax, fit_ymin, fit_ymax):
  """Initialize figures."""
  fig_ecsa = go.Figure()
  fig_ecsa.update_layout(xaxis_title='<b>Fixed Potential (V)</b>', yaxis_title='<b>log<sub>10</sub>( Current / ECSA )</b>', showlegend=True)
  fig_gsa = go.Figure()
  fig_gsa.update_layout(xaxis_title='<b>Fixed Potential (V)</b>', yaxis_title='<b>log<sub>10</sub>( Current / GSA )</b>', showlegend=True)

  """Draw traces."""
  if len(file_df>0):
    for i, (fig, norm) in enumerate(((fig_ecsa, ecsa_val), (fig_gsa, gsa_val))):
      x, y = np.abs(file_df.iloc[:,1]), np.log10(np.abs(file_df.iloc[:,2])/norm)
      trace = go.Scatter(x=x, y=y, mode='lines', line_color=styles.colors[i], name='Data')
      fig.add_trace(trace)

  """Draw fits."""
  if len(result_df>0):
    for i, (fig, norm) in enumerate(((fig_ecsa, ecsa_val), (fig_gsa, gsa_val))):
      x, y = result_df.iloc[:, 2*i], result_df.iloc[:,2*i+1]
      trace = go.Scatter(x=x, y=y, mode='lines', line_color=styles.colors[i], dash='dash', name='Fit')
      fig.add_trace(trace)

  """Draw contour line."""
  for fig in (fig_ecsa, fig_gsa):  # FIXME: change to filled region
    # trace = go.Scatter(x=[fit_xmin, fit_xmax, fit_xmax, fit_xmin, fit_xmin], y=[fit_ymin, fit_ymin, fit_ymax, fit_ymax, fit_ymin], mode='none', fill='tonext')
    trace = go.Scatter(x=[fit_xmin, fit_xmax, fit_xmax, fit_xmin, fit_xmin], y=[fit_ymin, fit_ymin, fit_ymax, fit_ymax, fit_ymin], mode='lines', line=dict(width=1, color='gray', dash='dash'), name='Fit range')
    fig.add_trace(trace)

    # fig.add_vline(
    #   x=fit_xmin, line_width=1, line_dash='dash', line_color='gray',
    #   annotation_text='Fit range min ', annotation_position='top left', annotation_font_size=12, annotation_font_color='gray',
    # )
    # fig.add_vline(
    #   x=fit_xmax, line_width=1, line_dash='dash', line_color='gray',
    #   annotation_text=' Fit range max', annotation_position='top right', annotation_font_size=12, annotation_font_color='gray',
    # )
    # fig.add_hline(
    #   y=fit_ymin, line_width=1, line_dash='dash', line_color='gray',
    #   annotation_text='Fit range y min ', annotation_position='bottom left', annotation_font_size=12, annotation_font_color='gray',
    # )
    # fig.add_hline(
    #   y=fit_ymax, line_width=1, line_dash='dash', line_color='gray',
    #   annotation_text=' Fit range y max', annotation_position='top left', annotation_font_size=12, annotation_font_color='gray',
    # )

  return fig_ecsa, fig_gsa

def build_tafel_inputs(app):
  content = list()

  """Parameters list."""
  file_uploader = dcc.Upload(
    id='tafel-upload',
    className='file-uploader',
    children=html.Div(['Drag-and-drop or ', html.A('select file', className='btn-link')]),
    multiple=False,
  )
  file_display = html.Div(id='tafel-file-display')
  storage = dcc.Store(data=dict(), id='tafel-file-storage', storage_type='memory')

  btn1 = dbc.InputGroup([
    dbc.InputGroupAddon('ECSA', addon_type='prepend'),
    dbc.Input(id='tafel-ecsa-input', value=1, type='number', required=True, step='any', placeholder='ECSA value'),
    dbc.InputGroupAddon('cm2', addon_type='append'),
  ])
  btn2 = dbc.InputGroup([
    dbc.InputGroupAddon('GSA', addon_type='prepend'),
    dbc.Input(id='tafel-gsa-input', value=1, type='number', required=True, step='any', placeholder='GSA value'),
    dbc.InputGroupAddon('cm2', addon_type='append'),
  ])
  btn3 = dbc.InputGroup([
    dbc.InputGroupAddon('pH', addon_type='prepend'),
    dbc.Input(id='tafel-ph-input', value=3, type='number', required=True, step='any', placeholder='pH level'),
  ])
  btn4 = dbc.InputGroup([
    dbc.InputGroupAddon('Ru', addon_type='prepend'),
    dbc.Input(id='tafel-ru-input', value=0, type='number', required=True, step='any', placeholder='Uncompensated resistance value'),
    dbc.InputGroupAddon('units', addon_type='append'),
  ])
  btn5a = dbc.InputGroup([
      dbc.InputGroupAddon('Fit range: x', addon_type='prepend'),
      dbc.Input(id='tafel-range-xmin-input', value=0, type='number', required=True, step='any', placeholder='x min'),
      dbc.Input(id='tafel-range-xmax-input', value=1, type='number', required=True, step='any', placeholder='x max'),
      dbc.InputGroupAddon('V', addon_type='append'),
    ],
  )
  btn5b = dbc.InputGroup([
      dbc.InputGroupAddon('Fit range: y', addon_type='prepend'),
      dbc.Input(id='tafel-range-ymin-input', value=0, type='number', required=True, step='any', placeholder='y min'),
      dbc.Input(id='tafel-range-ymax-input', value=1, type='number', required=True, step='any', placeholder='y max'),
      dbc.InputGroupAddon('units', addon_type='append'),
    ],
  )
  btn6 = dbc.InputGroup([
    dbc.InputGroupAddon("Fit method", addon_type="prepend"),
    dbc.Select(
      id='tafel-fitmethod-input',
      options=[
        {'label': 'Linear', 'value': 'linear'},
        {'label': 'Bayesian (julius)', 'value': 'julius'},
      ],
      value='linear',
      required=True,
      placeholder='Select fit method',
    ),
  ])
  btn_run = dbc.Button('Calculate Tafel slope', className='btn-block btn-primary', id='tafel-run-btn', n_clicks=0)

  content.append(dbc.Container([
    dbc.Row(dbc.Col([file_uploader, file_display, storage]), className='pb-1'),
    dbc.Row(dbc.Col(btn1), className='pb-1'),
    dbc.Row(dbc.Col(btn2), className='pb-1'),
    dbc.Row(dbc.Col(btn3), className='pb-1'),
    dbc.Row(dbc.Col(btn4), className='pb-1'),
    dbc.Row(dbc.Col(btn5a), className='pb-1'),
    dbc.Row(dbc.Col(btn5b), className='pb-1'),
    dbc.Row(dbc.Col(btn6), className='pb-1'),
    dbc.Row(dbc.Col(btn_run), className=''),
  ]))

  """Output display."""
  storage = dcc.Store(data=dict(), id='tafel-result-storage', storage_type='memory')
  download = html.Div([
    dbc.Button('Download fit results', id='tafel-download-button', className='btn-block btn-primary', n_clicks=0),
    dcc.Download(id='tafel-download-dataframe-csv'),
    storage,
  ])

  collapse_children = dbc.Container([
    dbc.Row(dbc.Col(id='tafel-ecsa-tafelslope-val')),
    dbc.Row(dbc.Col(id='tafel-gsa-tafelslope-val')),
    download,
  ])
  collapse = dbc.Collapse([html.Hr(), collapse_children], id='tafel-fit-output', is_open=False)
  content.append(collapse)

  @app.callback(
    Output('tafel-file-display', 'children'),
    Output('tafel-file-storage', 'data'),
    Output('tafel-range-xmin-input', 'value'),
    Output('tafel-range-xmax-input', 'value'),
    Output('tafel-range-ymin-input', 'value'),
    Output('tafel-range-ymax-input', 'value'),
    Output('tafel-ecsa-graph', 'figure'),
    Output('tafel-gsa-graph', 'figure'),
    Output('tafel-result-storage', 'data'),
    Output('tafel-ecsa-tafelslope-val', 'children'),
    Output('tafel-gsa-tafelslope-val', 'children'),
    Input('tafel-upload', 'filename'),
    Input('tafel-run-btn', 'n_clicks'),
    Input('tafel-range-xmin-input', 'value'),
    Input('tafel-range-xmax-input', 'value'),
    Input('tafel-range-ymin-input', 'value'),
    Input('tafel-range-ymax-input', 'value'),
    Input('tafel-ecsa-input', 'value'),
    Input('tafel-gsa-input', 'value'),
    Input('tafel-ph-input', 'value'),
    Input('tafel-ru-input', 'value'),
    State('tafel-fitmethod-input', 'value'),
    State('tafel-upload', 'contents'),
    State('tafel-file-storage', 'data'),
    State('tafel-result-storage', 'data'),
  )
  def tafel_fit_callback(new_file_name, run_btn_clicks, fit_xmin, fit_xmax, fit_ymin, fit_ymax, ecsa_val, gsa_val, ph, ru, fitmethod, new_file_content, file_storage, result_storage):
    ctx = dash.callback_context
    trig_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    """Get values from storage"""
    file_df = pd.DataFrame.from_dict(file_storage)
    result_df = pd.DataFrame.from_dict(result_storage)
    file_name = no_update
    norm_types = ['ecsa', 'gsa']
    tafel_slope_val = {n: no_update for n in norm_types}

    if trig_id == 'tafel-upload':  # New file uploaded
      f = StringIO(templates.parse_file(new_file_content))
      file_df = pd.read_table(f, header=(0))  # sep=',',
      file_df.insert(1, 'E_fixed/V', file_df.iloc[:, 0])  # Copy first column as a placeholder for corrected potential
      file_name = new_file_name

    if len(file_df) > 0:
      file_df.iloc[:, 1] = tafel_slope.correct_potential(file_df.iloc[:, 0], file_df.iloc[:, 2], ph, ru)
    if trig_id == 'tafel-upload':
      fit_xmin, fit_xmax = min(np.abs(file_df.iloc[:,1])), max(np.abs(file_df.iloc[:,1]))
      fit_ymin, fit_ymax = min(np.log10(np.abs(file_df.iloc[:,2]))), max(np.log10(np.abs(file_df.iloc[:,2])))

    if trig_id == 'tafel-run-btn':
      e, i = file_df.iloc[:, 1].to_numpy(), file_df.iloc[:, 2].to_numpy()
      mask = (np.abs(e)>=fit_xmin) & (np.abs(e)<=fit_xmax) & (np.log10(np.abs(i))>=fit_ymin) & (np.log10(np.abs(i))<=fit_ymax)
      for j, n in enumerate(norm_types):
        print(e[mask])
        print(i[mask]/n)
        if fitmethod == 'linear':
          slope_val, res_x, res_y = tafel_slope.fit_tafel_slope_linear(e[mask], i[mask]/n)
        elif fitmethod == 'julius':
          slope_val, res_x, res_y = tafel_slope.fit_tafel_slope_julius(e[mask], i[mask]/n)
        else:
          raise ValueError(f"Fit method '{fitmethod}' not implemented.")
        # Set values
        tafel_slope_val[n] = slope_val
        result_df.iloc[:, 2*j] = res_x
        result_df.iloc[:, 2*j+1] = res_y

    """Prepare return values."""
    file_storage = file_df.to_dict(orient='records')
    result_storage = result_df.to_dict(orient='records')
    fig_ecsa, fig_gsa = build_tafel_figs(file_df, result_df, ecsa_val, gsa_val, fit_xmin, fit_xmax, fit_ymin, fit_ymax)
    return file_name, file_storage, fit_xmin, fit_xmax, fit_ymin, fit_ymax, fig_ecsa, fig_gsa, result_storage, tafel_slope_val['ecsa'], tafel_slope_val['gsa']

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../docs/tafel.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'tafel', 'Tafel Slope Instructions', dcc.Markdown(txt))
  layout = templates.build_card('Inputs', content, info=info)
  return layout
