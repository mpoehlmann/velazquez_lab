import yaml
import os
import numpy as np


def load_yaml(fname):
    with open(fname, 'r') as f:
        yy = yaml.safe_load(f)

    return yy


def parse_record_id(fname):
    # record IDs are stored as YYY_ZZZ where YYY is the digits labeling the
    # paper the data was taken from, and ZZZ is the digits labeling the figure
    # inside that paper
    bname = os.path.basename(fname)
    split = bname.split('_')
    split = split[1].split('.')
    record_id = int(split[0])
    return record_id


class TafelRecord:
    def __init__(self, data_fname, mdata_fname, identifier):
        # save the filename arguments
        self.mdata_fname = mdata_fname
        self.data_fname = data_fname

        # load up the metadata file and the data file
        self.mdata = load_yaml(mdata_fname)
        self.data = np.loadtxt(data_fname, delimiter=',')

        # store the unique identifier
        self.identifier = identifier

        # sanitize the current and voltage records
        self.s_voltage, self.s_current = self._sanitize_data()

        # extract the reported tafel slope and possibly a reported error as
        # well
        self.r_tafel = self.mdata['rval']
        self.r_tafel_err = self.mdata['rerr']

    def _sanitize_data(self):
        xdat = self.data[:, 0]
        ydat = self.data[:, 1]

        # get the current and voltage assigned properly, take the logarithm of
        # the current if it hasn't already been done, also normalize the
        # voltage units to just volts
        if self.mdata['xdat'] == 'current':
            current = xdat
            voltage = ydat

            if not self.mdata['xlog']:
                current = np.log10(current)

            if self.mdata['yunit'] == 'mV':
                voltage = voltage * 1e-3
            elif self.mdata['yunit'] == 'V':
                pass
            else:
                raise ValueError('bad voltage unit in metadata file %s' % self.mdata_fname)

        elif self.mdata['ydat'] == 'current':
            voltage = xdat
            current = ydat

            if not self.mdata['ylog']:
                current = np.log10(current)

            if self.mdata['xunit'] == 'mV':
                voltage = voltage * 1e-3
            elif self.mdata['xunit'] == 'V':
                pass
            else:
                raise ValueError('bad voltage unit in metadata file %s' % self.mdata_fname)

        else:
            raise ValueError('bad metadata file %s' % self.mdata_fname)

        # fix reversal issues
        if self.mdata['v_reversed']:
            voltage = -voltage

        if self.mdata['i_reversed']:
            current = -current

        return voltage, current
