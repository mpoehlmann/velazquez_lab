"""Create user interface for GSA section of polarization curve analysis.
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


def build_gsa_inputs(app):
  content = list()

  content.append(html.H1('TODO'))

  """Layout."""
  fpath = os.path.dirname(os.path.realpath(__file__))
  f = open(f"{fpath}/../../docs/gsa.md", 'r')
  txt = f.read()
  info = templates.build_modal(app, 'gsa', 'GSA Instructions', dcc.Markdown(txt))
  layout = templates.build_card('Inputs', content, info=info)
  return layout


