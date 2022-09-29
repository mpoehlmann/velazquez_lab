"""
Analysis dashboard. This is a graphical user interface (GUI) for user-friendly data analysis.
Notes:
  This is the suggested way to setup a Dash app, not nested within a class.
"""
import argparse
from velazquez_lab.app.main import build_app


def parse_args():
  """Parse commandline arguments for module."""
  ap = argparse.ArgumentParser()
  ap.add_argument('-d', '--debug', default=False, action='store_true', help='Control application debugging')
  ap.add_argument('--host', default='127.0.0.1', help='Specify host')
  ap.add_argument('-p', '--port', default=8050, type=int, help='Specify application port')
  ap.add_argument('-t', '--theme', default='light', help='Specify light or dark theme')
  args = vars(ap.parse_args())
  return args


if __name__ == '__main__':
  """Run application.
  To run:
    python app.py
    python app.py -d
    python app.py -t dark
  """
  args = parse_args()
  app = build_app(theme=args['theme'], jupyter=False)
  app.run_server(debug=args['debug'], host=args['host'], port=args['port'])
