"""Analysis dashboard. This is a graphical user interface (GUI) for user-friendly data analysis.
Notes:
  This is the suggested way to setup a Dash app, not nested within a class.
"""

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
from velazquez_lab.plot import styles


styles.set_plotly_style('light')


def build_app(start_page=1, theme='light', jupyter=False):
  """Setup application."""
  styles.set_plotly_style(theme)

  external_stylesheets = [
    "https://use.fontawesome.com/releases/v5.15.3/css/all.css",
    # "https://codepen.io/rmarren1/pen/mLqGRg.css",
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
    dict(id='pg-pol', label='Polarization curves', content=create_pol_page(app)),
    # dict(id='id_2', label='Label 2', content=create_pol_page),
    # dict(id='id_3', label='Label 3', content=create_pol_page),
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


if __name__ == '__main__':
  """Run application.
  To run:
    python app.py
    python app.py -t dark
  """
  import argparse
  ap = argparse.ArgumentParser()
  ap.add_argument('-b', '--binder', default=False, action='store_true', help='Enable running from Binder')
  ap.add_argument('-d', '--debug', default=False, action='store_true', help='Control application debugging')
  ap.add_argument('--host', default='127.0.0.1', help='Specify host')
  ap.add_argument('-p', '--port', default=8050, type=int, help='Specify application port')
  ap.add_argument('-t', '--theme', default='light', help='Specify light or dark theme')
  args = vars(ap.parse_args())

  app = build_app(theme=args['theme'], jupyter=False)
  if args['binder']:
    app.run_server(debug=args['debug'], port=args['port'])
  else:
    app.run_server(debug=args['debug'], host=args['host'], port=args['port'])



