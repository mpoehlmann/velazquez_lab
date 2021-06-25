"""Create user interface for POL section of polarization curve analysis.
See pol_page.py for usage.
"""

import dash
from dash.dash import no_update, PreventUpdate
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


def build_pol_inputs(app):
  content = list()

  """Parameters list."""
  btn1 = dbc.InputGroup([
    dbc.InputGroupAddon('ECSA', addon_type='prepend'),
    dbc.Input(id='pol-ecsa-input', value=1, type='number', step='any', placeholder='ECSA value'),
    dbc.InputGroupAddon('units', addon_type='append'),
  ])
  btn2 = dbc.InputGroup([
    dbc.InputGroupAddon('GSA', addon_type='prepend'),
    dbc.Input(id='pol-gsa-input', value=1, type='number', step='any', placeholder='GSA value'),
    dbc.InputGroupAddon('units', addon_type='append'),
  ])
  btn3 = dbc.InputGroup([
    dbc.InputGroupAddon('pH', addon_type='prepend'),
    dbc.Input(id='pol-ph-input', value=3, type='number', step='any', placeholder='pH level'),
  ])
  btn4 = dbc.InputGroup([
    dbc.InputGroupAddon('Ru', addon_type='prepend'),
    dbc.Input(id='pol-ru-input', value=0, type='number', step='any', placeholder='Uncompensated resistance value'),
    dbc.InputGroupAddon('units', addon_type='append'),
  ])
  btn_load = dbc.InputGroup([
    # dbc.InputGroupAddon('File', addon_type='prepend'),
    dbc.Input(id='pol-file-input', value='data/sample_1/1-12-2021_K2Mo6Te8_sample1_her_10_LSV_C03.txt', type='text', placeholder='File path and name'),
    dbc.InputGroupAddon(
      dbc.Button('Load data', className='btn-primary', id='pol-load-button', n_clicks=0),
      addon_type='append'
    ),
  ])

  content.append(dbc.Container([
    dbc.Row(dbc.Col(btn1), className='pb-1'),
    dbc.Row(dbc.Col(btn2), className='pb-1'),
    dbc.Row(dbc.Col(btn3), className='pb-1'),
    dbc.Row(dbc.Col(btn4), className='pb-1'),
    dbc.Row(dbc.Col(btn_load)),
  ]))




  @app.callback(
    Output('pol-ecsa-graph', 'figure'),
    Output('pol-gsa-graph', 'figure'),
    Output('pol-ecsa-output', 'children'),
    Output('pol-gsa-output', 'children'),
    Input('pol-load-button', 'n_clicks'),
    Input('pol-run-button', 'n_clicks'),
    State('pol-file-input', 'value'),
    State('pol-ecsa-input', 'value'),
    State('pol-gsa-input', 'value'),
    State('pol-ph-input', 'value'),
    State('pol-ru-input', 'value'),
    State('pol-fitmethod-input', 'value'),
    State('pol-range-min-input', 'value'),
    State('pol-range-max-input', 'value'),
    State('pol-ecsa-graph', 'figure'),
    State('pol-gsa-graph', 'figure'),
  )
  def on_pol_load_button_click(n1, n2, file, ecsa_val, gsa_val, ph, ru, fitmethod, xmin, xmax, fig_ecsa, fig_gsa):
    ctx = dash.callback_context
    if not ctx.triggered:
      button_id = 'none'
    else:
      button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id=='pol-load-button' or button_id=='none':
      fig_ecsa, fig_gsa = ( go.Figure() for _ in range(2) )
      fig_ecsa.update_layout(xaxis_title='<b>Potential (V)</b>', yaxis_title='<b>log<sub>10</sub>( Current / ECSA )</b>', showlegend=True)
      fig_gsa.update_layout(xaxis_title='<b>Potential (V)</b>', yaxis_title='<b>log<sub>10</sub>( Current / GSA )</b>', showlegend=True)
      if button_id=='none' or n1<1:
        return fig_ecsa, fig_gsa, f"Tafel slope (ECSA) =", f"Tafel slope (GSA) ="

      df = pol_curves.load_data(file)
      df = pol_curves.correct_potential(df, ph, ru)
      df.insert(3, 'I_ECSA', df['I']/ecsa_val)
      df.insert(4, 'I_GSA', df['I']/gsa_val)
      pol_objs['df'] = df

      for i, (method, fig) in enumerate(zip(['ECSA', 'GSA'], [fig_ecsa, fig_gsa])):
        x, y = df['E_fixed'], np.log10(df[f'I_{method}'])
        trace = go.Scatter(x=x, y=y, mode='lines', line_color=styles.colors[i], name='Data')
        pol_objs[method]['gr'] = trace
        fig.add_trace(trace)

      return fig_ecsa, fig_gsa, f"Tafel slope (ECSA) =", f"Tafel slope (GSA) ="

    elif button_id=='pol-run-button':
      if n2 < 1:
        return fig_ecsa, fig_gsa, f"Tafel slope (ECSA) =", f"Tafel slope (GSA) ="

      df = pol_objs['df']
      mask = (df['E_fixed']>=xmin) & (df['E_fixed']<=xmax)
      m, b, rsq = (dict() for _ in range(3))
      for i, (method, fig) in enumerate(zip(['ECSA', 'GSA'], [fig_ecsa, fig_gsa])):
        x, y = df['E_fixed'][mask], df[f'I_{method}'][mask]
        if fitmethod == 'julius':
          cidx = 2
          tr_name = 'Bayesian fit'
          m[method], fitres_x, fitres_y = pol_curves.fit_tafel_slope_julius(x, y)
        elif fitmethod == 'user':
          cidx = 4
          tr_name = 'linear fit'
          m[method], fitres_x, fitres_y = pol_curves.fit_tafel_slope_linear(x, y)
        else:
          raise ValueError(f"Fit method ('{fitmethod}') not implemented.")

        trace = go.Scatter(x=fitres_x, y=fitres_y, mode='lines', line=dict(color=styles.colors[cidx+i], dash='dash'), name=tr_name)
        pol_objs[method][f'fitres_{fitmethod}_gr'] = trace

        # Reset figure data
        fig['data'] = [ pol_objs[method]['gr'] ]
        for fitmethod in ['julius', 'user']:
          key = f'fitres_{fitmethod}_gr'
          if pol_objs[method].get(key) is not None:
            fig['data'].append( pol_objs[method][key] )

      return fig_ecsa, fig_gsa, f"Tafel slope (ECSA) = {m['ECSA']:.5f}", f"Tafel slope (GSA) = {m['GSA']:.5f}"

    else:
      raise ValueError(f"Button ID ({button_id}) not implemented.")


  content.append(html.Hr())

  obj = dbc.InputGroup([
      dbc.InputGroupAddon("Fit method", addon_type="prepend"),
      dbc.Select(
        id='pol-fitmethod-input',
        options=[
          {'label': 'Bayesian (julius)', 'value': 'julius'},
          {'label': 'User defined range', 'value': 'user'},
        ],
        value='julius',
        placeholder='Select fit method',
      ),
    ],
  )
  content.append(html.Div(obj))

  obj = dbc.InputGroup([
      dbc.InputGroupAddon('User fit range', addon_type='prepend'),
      dbc.Input(id='pol-range-min-input', value=0.87, type='number', step='any', placeholder='Min'),
      dbc.Input(id='pol-range-max-input', value=1.006, type='number', step='any', placeholder='Max'),
      dbc.InputGroupAddon('V', addon_type='append'),
    ],
  )
  content.append(html.Div(obj))

  """Run button."""
  obj = dbc.Button('Calculate Tafel slope', className='btn-block btn-primary', id='pol-run-button', n_clicks=0)
  content.append(html.Div(obj))

  content.append(html.Hr())

  content.append(dbc.Alert(id='pol-ecsa-output', className="alert-success"))
  content.append(dbc.Alert(id='pol-gsa-output', className="alert-success"))

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../assets/docs/pol.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'pol', 'Polarization Curve Instructions', dcc.Markdown(txt))
  layout = templates.build_card('Inputs', content, info=info)
  return layout
