"""Create user interface for polarization curve analysis.
See app.py for usage.
"""

import dash_bootstrap_components as dbc
import dash_html_components as html

from velazquez_lab.app import ecsa_section, tafel_section


def create_pol_page(app):
  pg = dbc.Container(
    [
      html.Div('Electrochemical Surface Area', className='section-header mb-1'),
      ecsa_section.build_ecsa_row(app),
      html.Hr(className='section-hr'),
      html.Div('Polarization Curves & Tafel Slope', className='section-header mb-1'),
      tafel_section.build_tafel_row(app),
      html.Hr(className='section-hr'),
    ],
    className='page-content',
    fluid=True
  )

  return pg