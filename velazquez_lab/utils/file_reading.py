"""File reading functions."""

import base64
from io import StringIO
import openpyxl
import pandas as pd


def load_excel_ws(file, sheet):
  """Load worksheet from an .xlsx file. Excel column and row labeling is matched."""
  df = pd.read_excel(file, sheet, header=None)
  df.rename(columns={c: openpyxl.utils.cell.get_column_letter(c+1) for c in df.columns}, inplace=True)
  df.set_index(df.index + 1, inplace=True)
  return df


def parse_dash_file(contents):
  """Parse the contents of a file from dash."""
  # print(contents)
  content_type, content_string = contents.split(',')
  decoded = base64.b64decode(content_string)
  return StringIO(decoded.decode('utf-8'))