"""File utilities."""

import os
import re


def get_files(path=None, pattern='', ext='', nreq=None):
  """Find all files matching the desired criteria.
  Args:
    path (str, None): directory in which files will be searched for
    pattern (str): regular expression for file name selection
    ext (str): file extension
    nreq (int, None): number of required files to be found
  Returns:
    files (list, str): list of all files in the path matching the given criteria
  """
  files = os.listdir(path)
  files.sort()

  if pattern:
    files = [f for f in files if re.match(pattern, f)]
  if ext:
    ext = ext.lower().replace('.', '')  # Remove dot if specified
    files = [f for f in files if re.match(r'.*\.'+ext, f)]

  if nreq is not None:
    if len(files) != nreq:
      raise OSError(f"More than one file found for pattern:\n  {fname}")
    if nreq == 1:  # If one file specified, then return str instead of list
      return files[0]
  return files