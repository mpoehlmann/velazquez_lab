"""Analysis dashboard. This is a graphical user interface (GUI) for user-friendly data analysis.
Notes:
  This is the suggested way to setup a Dash app, not nested within a class.
"""

import dash
from jupyter_dash import JupyterDash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import pandas as pd

from velazquez_lab.app import templates
from velazquez_lab.app.pol_page import create_pol_page
from velazquez_lab.app.filt_page import create_filt_page
from velazquez_lab.plot import styles


styles.set_plotly_style('light')


def build_app(start_page=0, theme='light', jupyter=False):
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
    dict(id='pg-filt', label='Filtering', content=create_filt_page),
    dict(id='pg-pol', label='Polarization curves', content=create_pol_page),
    # dict(id='id_2', label='Label 2', content=create_pol_page),
    # dict(id='id_3', label='Label 3', content=create_pol_page),
  ])

  def create_page(i):
    return [templates.build_navbar(app, pages, i, subtitle='Data Analysis Toolkit'), pages.loc[i, 'content'](app)]


  """Create layout and setup page loading."""
  app.layout = html.Div(create_page(start_page), id='page-content')

  @app.callback(
    Output("page-content", "children"),
    *(Input(pid, 'n_clicks_timestamp') for pid in pages['id']),
  )
  def toggle_collapse(c, *inputs):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    if button_id is None:
      raise PreventUpdate
    for i, p in enumerate(pages.itertuples()):
      if p.id == button_id:
        return create_page(i)

  return app


if __name__ == '__main__':
  """Run application.
  To run:
    python app.py
    python app.py -t dark
  """
  import argparse
  ap = argparse.ArgumentParser()
  ap.add_argument('-t', '--theme', default='light', help='Specify light or dark theme')
  args = vars(ap.parse_args())

  app = build_app(**args)
  app.run_server(debug=True, host='127.0.0.1')



