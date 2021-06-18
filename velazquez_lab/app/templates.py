"""Template objects for Dash application."""

import base64
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
import dash_html_components as html


def parse_file(contents):
  # print(contents)
  content_type, content_string = contents.split(',')
  decoded = base64.b64decode(content_string)
  return decoded.decode('utf-8')


def build_modal(app, name, title, content):
  open_button = html.I(className='far fa-question-circle', n_clicks=0, id=f"open-{name}")
  close_button = html.I(className='far fa-window-close', n_clicks=0, id=f"close-{name}")
  modal = dbc.Modal(
    [
      dbc.ModalHeader([html.Div(title, className='flex-1'), close_button]),
      dbc.ModalBody(content),
    ],
    id=f"modal-{name}",
  )

  @app.callback(
    Output(f"modal-{name}", "is_open"),
    Input(f"open-{name}", "n_clicks"),
    Input(f"close-{name}", "n_clicks"),
    State(f"modal-{name}", "is_open"),
  )
  def toggle_modal(n1, n2, is_open):
    if n1 or n2:
      return not is_open
    return is_open

  return open_button, modal


def build_card(title, content, info=None):
  if info is not None:
    header = dbc.CardHeader([title, *info])
  else:
    header = dbc.CardHeader(title)

  card = dbc.Card(
    [
      header,
      dbc.CardBody(content),
    ],
    className='h-100',
  )
  return card


def build_navbar(app, pages, active_page=0, subtitle=None):
  dropdown = dbc.DropdownMenu(
    children=[dbc.DropdownMenuItem(p.label, id=p.id) for p in pages.itertuples()],
    in_navbar=True,
    label='Tools',
    # label=html.I(className='far fa-question-circle', n_clicks=0, id=f"open-{name}"),
    # className='fas fa-bars pl-1'
    className='site-menu',
    right=True,
    color='dark',
  )

  t = [ dbc.NavbarBrand(app.title, className='m-0 p-0', style={'textTransform': 'uppercase', 'fontSize': '20px'}) ]
  if subtitle is not None:
    t.append( dbc.NavbarBrand(subtitle, className='m-0 p-0', style={'fontSize': '15px'}) )

  navbar = dbc.Navbar(
    children=[
      html.Div(html.Img(src=app.get_asset_url('images/logo.png'), height='40px'), className='px-2'),
      html.Div(t, className='d-flex flex-column flex-grow-1 pl-2'),
      html.Div(dbc.NavbarBrand(pages.loc[active_page, 'label'])),
      html.Div(dropdown, className='p-1'),
    ],
    className='d-flex align-items-center p-2',
    color='secondary',
    dark=True,
  )

  return navbar
