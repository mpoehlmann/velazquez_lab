"""Analysis dashboard. This is a graphical user interface (GUI) for user-friendly data analysis.
Notes:
  This is the suggested way to setup a Dash app, not nested within a class.
"""

import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import pandas as pd

from velazquez_lab.app import templates
from velazquez_lab.app.pol_page import create_pol_page
from velazquez_lab.plot import styles


styles.set_plotly_style('light')

"""Setup application."""
app = dash.Dash(
  __name__,
  title = 'Velázquez Lab',
  external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css",
    "https://use.fontawesome.com/releases/v5.15.3/css/all.css",
    # "https://codepen.io/rmarren1/pen/mLqGRg.css",
  ],
)


"""Define pages."""
pages = pd.DataFrame([
  dict(id='pg_pol', label='Polarization curves', content=create_pol_page),
  # dict(id='id_2', label='Label 2', content=create_pol_page),
  # dict(id='id_3', label='Label 3', content=create_pol_page),
])

def create_page(i):
  return [templates.build_navbar(app, pages, i, subtitle='Data Analysis Toolkit'), pages.loc[i, 'content'](app)]


"""Create layout and setup page loading."""
app.layout = html.Div(create_page(0), id='page-content')

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



if __name__ == '__main__':
  """Run application.
  To run:
    python app.py
  """
  app.run_server(debug=True, host='127.0.0.1')



