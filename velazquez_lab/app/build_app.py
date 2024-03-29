
import dash
from jupyter_dash import JupyterDash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd

from velazquez_lab.app import templates
from velazquez_lab.app.pol_page import create_pol_page
from velazquez_lab.app.filt_page import create_filt_page
from velazquez_lab.app.linfit_page import create_linfit_page
from velazquez_lab.utils import styles


def build_app(start_page=2, theme='light', jupyter=False):
  """Setup application."""
  styles.set_plotly_style(theme)

  external_stylesheets = [
    "https://use.fontawesome.com/releases/v5.15.3/css/all.css",
  ]
  if theme == 'light':
    external_stylesheets.append('https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css')
  elif theme == 'dark':
    external_stylesheets.append('https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/darkly/bootstrap.min.css')
  else:
    raise ValueError(f"Theme {theme} not yet implemented.")

  dash_args = dict(
    title='Velázquez Lab',
    external_stylesheets=external_stylesheets,
  )
  app = JupyterDash(__name__, **dash_args) if jupyter else dash.Dash(__name__, **dash_args)

  """Define pages."""
  pages = pd.DataFrame([
    dict(id='pg-filt', label='Filtering', content=create_filt_page(app)),
    dict(id='pg-linfit', label='Linear fitting', content=create_linfit_page(app)),
    dict(id='pg-pol', label='Polarization curves', content=create_pol_page(app)),
  ])


  """Create layout and setup page loading."""
  def create_page(button_id):
    for i, p in enumerate(pages.itertuples()):
      if p.id == button_id:
        header = dbc.NavbarBrand(p.label)
        return p.content, header
    return html.H1("404: page ID not found."), None

  full_page = html.Div([
    templates.build_navbar(app, pages, start_page, subtitle='Data Analysis Toolkit'),
    html.Div(create_page(pages.loc[start_page, 'id']), id='main-page'),
  ])

  """Index layout."""
  app.layout = full_page

  """Complete layout."""
  app.validation_layout = html.Div([
    full_page,
    *(c for c in pages['content']),
  ])

  @app.callback(
    Output('main-page', 'children'),
    Output('navbar-page-name', 'children'),
    *(Input(pid, 'n_clicks_timestamp') for pid in pages['id']),
    # prevent_initial_call=True,
  )
  def load_page(*inputs):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    if button_id is None:
      button_id = pages.loc[start_page, 'id']
    return create_page(button_id)

  return app