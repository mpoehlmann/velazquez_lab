"""Configuration file parser."""

from configparser import ConfigParser
import numericalunits as nu
import numpy as np


def parse_config(fname):
  """Parses configuration file. This allows for units to be added with the numericalunits package and for objects like lists to be easily used.
  Args:
    fname: configuration file name
  Notes:
    If using units, be sure to put 'nu.' before the unit.
  """
  # Parse configuration
  conf = ConfigParser()
  conf.read(fname)

  # Convert to dictionary format and parse data type
  conf_dict = dict()
  for sname, sect in conf.items():
    conf_dict[sname] = dict()
    for key,val in sect.items():
      conf_dict[sname][key] = eval(val, {'nu':nu, 'np':np})  # This is safe to use since input strings are trusted. Don't use eval() on configuration files from untrusted sources.

  return conf_dict