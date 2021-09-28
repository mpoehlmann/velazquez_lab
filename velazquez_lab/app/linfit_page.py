"""Create user interface for linear fitting.
See app.py for usage.
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
import uncertainties as un
from uncertainties import unumpy as unp

from velazquez_lab.app import templates
from velazquez_lab.utils.file_reading import parse_dash_file
from velazquez_lab.utils import styles
from velazquez_lab.utils import linear_fitting as ft


def create_linfit_figs(data_df, output_df):
  fig_linfit = go.Figure()
  fig_linfit.update_layout(xaxis_title='<b>x</b>', yaxis_title='<b>y</b>', showlegend=False)

  fig_chi = go.Figure()
  fig_chi.update_layout(xaxis_title='<b>Data point</b>', yaxis_title='<b>Chi</b>')

  if len(data_df) > 0:
    data_df = data_df.sort_values('x', inplace=False)

    tr = go.Scatter(
      x=data_df['x'],
      y=data_df['y'],
      error_x=dict(type='data', array=data_df['x_err'], visible=True, width=0),
      error_y=dict(type='data', array=data_df['y_err'], visible=True, width=0),
      mode='markers',
      marker_color=styles.COLORS[0],
      name=f"<b>Data</b>",
    )
    fig_linfit.add_trace(tr)

  if len(output_df) > 0:
    m_fit = un.ufloat(output_df.loc[0, 'm'], output_df.loc[0, 'm_err'])
    b_fit = un.ufloat(output_df.loc[0, 'b'], output_df.loc[0, 'b_err'])
    interval = data_df['x'].max() - data_df['x'].min()
    x_fit = np.linspace(data_df['x'].min()-0.1*interval, data_df['x'].max()+0.1*interval, 101)
    y_fit = ft.linear_eqn(unp.uarray(x_fit, np.zeros(x_fit.size)), m=m_fit, b=b_fit)

    tr1 = go.Scatter(x=x_fit, y=unp.nominal_values(y_fit), mode='lines', line_color=styles.COLORS[1], name=f"<b>Fit</b>")
    fig_linfit.add_trace(tr1)
    tr2 = go.Scatter(x=x_fit, y=unp.nominal_values(y_fit)-unp.std_devs(y_fit), mode='lines', line_color=styles.color_to_rgba(styles.COLORS[1], 0))
    fig_linfit.add_trace(tr2)
    tr3 = go.Scatter(x=x_fit, y=unp.nominal_values(y_fit)+unp.std_devs(y_fit), mode='lines', fill='tonexty', line_color=styles.color_to_rgba(styles.COLORS[1], 0))  # , fill_color=styles.color_to_rgba(styles.COLORS[1], 0.4))
    fig_linfit.add_trace(tr3)

    # Calculate chi values.
    _m, _b = (m_fit.n, b_fit.n)
    chi = data_df['y'] - ft.linear_eqn(data_df['x'], _m, _b)
    is_x_err = not (data_df['x_err'] == 0).all()
    is_y_err = not (data_df['y_err'] == 0).all()
    if is_x_err and is_y_err:
      wt_sq = _m**2*data_df['x_err']**2 + data_df['y_err']**2
    elif is_x_err:
      wt_sq = _m**2 * data_df['x_err']**2
    elif is_y_err:
      wt_sq = data_df['y_err']**2
    else:
      wt_sq = np.ones(data_df['x'].size)
    chi /= np.sqrt(wt_sq)

    tr = go.Bar(x=np.arange(chi.size), y=chi)
    fig_chi.add_trace(tr)
  return fig_linfit, fig_chi


def create_linfit_page(app):
  file_uploader = dcc.Upload(
    id='linfit-upload',
    className='file-uploader',
    children=html.Div(['Drag-and-drop or ', html.A('select file', className='btn-link')]),
    multiple=False,
  )
  table = dash_table.DataTable(
    id='linfit-data-table',
    columns=[
      {'name': 'x', 'id': 'x', 'type': 'numeric',},
      {'name': 'x errors', 'id': 'x_err', 'type': 'numeric',},
      {'name': 'y', 'id': 'y', 'type': 'numeric',},
      {'name': 'y errors', 'id': 'y_err', 'type': 'numeric',},
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
    editable=True,
    row_deletable=True,
  )
  btn_row = dbc.Button('Add row', n_clicks=0, id='linfit-addrow-btn', className='btn-block btn-primary mr-1')

  output_storage = dcc.Store(data=dict(), id='linfit-output-storage', storage_type='memory')
  btn_fit = dbc.Button('Fit', n_clicks=0, id='linfit-fit-btn', className='btn-block btn-primary mr-1')

  @app.callback(
    Output('linfit-data-table', 'data'),
    Output('linfit-output-storage', 'data'),
    Output('linfit-graph', 'figure'),
    Output('linfit-chi-graph', 'figure'),
    Output('linfit-fit-eqn', 'children'),
    Output('linfit-fit-chisq', 'children'),
    Input('linfit-upload', 'contents'),
    Input('linfit-addrow-btn', 'n_clicks'),
    Input('linfit-fit-btn', 'n_clicks'),
    # Input('linfit-download-button', 'n_clicks'),
    State('linfit-data-table', 'data'),
    State('linfit-data-table', 'columns'),
    State('linfit-output-storage', 'data'),
  )
  def linfit_callback(new_file_content, n_clicks_adrow, n_clicks_fit, data_df, data_columns, output_df):  # n_clicks_download,
    """Link filtering elements together."""
    """Get id of component which triggered the callback."""
    ctx = dash.callback_context
    trig_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    data_df = pd.DataFrame.from_dict(data_df)
    if len(data_df.columns) == 0:
      data_df = pd.DataFrame(columns=[c['id'] for c in data_columns])
    data_df['x_err'].fillna(0, inplace=True)
    data_df['y_err'].fillna(0, inplace=True)
    output_df = pd.DataFrame.from_dict(output_df)
    linfit_eqn = ''
    redchi_text = ''

    if trig_id == 'linfit-upload':
      f = parse_dash_file(new_file_content)
      data_df = pd.read_table(f, header=0, sep=',')

    elif trig_id == 'linfit-addrow-btn':
      data_df = data_df.append(pd.Series({c: None for c in data_df.columns}), ignore_index=True)

    elif trig_id == 'linfit-fit-btn':
      x_err = None if (data_df['x_err'] == 0).all() else data_df['x_err']
      y_err = None if (data_df['y_err'] == 0).all() else data_df['y_err']
      m_fit, b_fit, redchi = ft.linear_fit(data_df['x'], data_df['y'], x_err=x_err, y_err=y_err, is_verbose=True)
      output_df = pd.DataFrame.from_dict({
        'm': [m_fit.n],
        'm_err': [m_fit.s],
        'b': [b_fit.n],
        'b_err': [b_fit.s],
        'redchi': [redchi],
      })
      linfit_eqn = f'y = {m_fit} x  +  {b_fit}'
      redchi_text = f'Reduced chi-squared = {redchi:.4g}'

    elif trig_id == 'ecsa-download-button':
      pass

    fig_linfit, fig_chi = create_linfit_figs(data_df, output_df)
    outputs = tuple([
      data_df.to_dict(orient='records'),
      output_df.to_dict(orient='records'),
      fig_linfit,
      fig_chi,
      linfit_eqn,
      redchi_text,
    ])
    return outputs

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../docs/linear_fitting.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'linfit', 'Linear Fitting Instructions', dcc.Markdown(txt))
  inputs = templates.build_card(
    'Inputs',
    dbc.Container([
      html.Div(file_uploader, className='pb-1'),
      html.Div(table),
      html.Div(btn_row, className='pb-1'),
      html.Div(btn_fit, className='pb-1'),
      output_storage,
    ]),
    info=info
  )

  pg = dbc.Container(
    [
      html.Div('Linear Fitting', className='section-header mb-1'),
      dbc.Row([
        dbc.Col(inputs, className='col-4'),
        dbc.Col(templates.build_card('Graph', [dcc.Graph(id='linfit-graph'), html.Div(id='linfit-fit-eqn'), html.Div(id='linfit-fit-chisq')]), className='col-4'),
        dbc.Col(templates.build_card('Graph', dcc.Graph(id='linfit-chi-graph')), className='col-4'),
      ]),
      html.Hr(className='section-hr'),
    ],
    className='page-content',
    fluid=True
  )
  return pg