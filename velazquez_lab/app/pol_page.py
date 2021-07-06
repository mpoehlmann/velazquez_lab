"""Create user interface for polarization curve analysis.
See app.py for usage.
"""

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from velazquez_lab.app import templates, ecsa_section, gsa_section, tafel_section


def create_pol_page(app):
  ecsa_row = ecsa_section.build_ecsa_row(app)
  tafel_row = tafel_section.build_tafel_row(app)

  pg = templates.build_page(
    sections={
      'Electrochemical Surface Area': ecsa_row,
      # 'Geometric Surface Area': gsa_row,
      'Polarization Curves & Tafel Slope': tafel_row,
    }
  )

  return pg