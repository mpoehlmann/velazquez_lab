"""Create user interface for polarization curve analysis.
See app.py for usage.
"""

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from velazquez_lab.app import templates, ecsa_section, gsa_section, pol_section


def create_pol_page(app):
  ecsa_row = [
    dbc.Col(ecsa_section.build_ecsa_inputs(app), className='col-3'),
    dbc.Col(templates.build_card('Double-layer capacitance', dcc.Graph(id='ecsa-dlc-graph')), className='col-4half',),
    dbc.Col(templates.build_card('Fit results', dcc.Graph(id='ecsa-fit-graph')), className='col-4half',),
  ]

  # gsa_row = [
  #   dbc.Col(gsa_section.build_gsa_inputs(app), className='col-3',),
  #   dbc.Col(templates.build_card('Graph', dcc.Graph(id='gsa-graph')), className='col-4half',),
  #   # dbc.Col(templates.build_card('GSA-normalized', dcc.Graph(id='gsa-graph')), className='col-4half',),
  # ]

  pol_row = [
    dbc.Col(pol_section.build_pol_inputs(app), className='col-3',),
    dbc.Col(templates.build_card('ECSA-normalized', dcc.Graph(id='pol-ecsa-graph')), className='col-4half',),
    dbc.Col(templates.build_card('GSA-normalized', dcc.Graph(id='pol-gsa-graph')), className='col-4half',),
  ]

  pg = templates.build_page(
    sections={
      'Electrochemical Surface Area': ecsa_row,
      # 'Geometric Surface Area': gsa_row,
      'Tafel Slope': pol_row,
    }
  )

  return pg