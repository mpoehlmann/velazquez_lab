import numpy as np


def load_and_sanitize_data(fname):
    # load the data
    dat = np.loadtxt(fname)

    # sort the data by ascending voltage
    sort_perm = np.argsort(dat[:, 1])[::-1]
    dat = dat[sort_perm]

    # pull out the voltages and log currents
    log_current = dat[:, 0]
    voltages = -1 * dat[:, 1]

    return voltages, log_current
