"""Create user interface for polarization curve analysis.
See app.py for usage.
"""

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from velazquez_lab.app import templates, ecsa_section, pol_section


def create_pol_page(app):
  ecsa_row = dbc.Row(
    [
      dbc.Col(
        ecsa_section.build_ecsa_inputs(app),
        className='col-3',
      ),
      dbc.Col(
        templates.build_card('ECSA: Double-layer capacitance', dcc.Graph(id='ecsa-dlc-graph')),
        className='col-4half',
      ),
      dbc.Col(
        templates.build_card('ECSA: Fit results', dcc.Graph(id='ecsa-fit-graph')),
        className='col-4half',
      ),
    ],
  )

  pol_row = dbc.Row(
    [
      dbc.Col(
        pol_section.build_pol_inputs(app),
        className='col-3',
      ),
      dbc.Col(
        templates.build_card('POL: ECSA-normalized', dcc.Graph(id='pol-ecsa-graph')),
        className='col-4half',
      ),
      dbc.Col(
        templates.build_card('POL: GSA-normalized', dcc.Graph(id='pol-gsa-graph')),
        className='col-4half',
      ),
    ],
  )

  pg = dbc.Container(
    [
      html.Div('ECSA calculation', className='section-header mb-1'),
      ecsa_row,
      html.Hr(),
      html.Div('Tafel slope calculation', className='section-header mb-1'),
      pol_row,
    ],
    className='page-content',
    fluid=True
  )
  return pg