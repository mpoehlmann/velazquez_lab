import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


LOGE10 = np.log(10)
LOG10E = np.log10(np.exp(1))


def densely_sample_array(x, npts=100):
    dense = np.linspace(np.min(x), np.max(x), npts)
    dense_offset = dense - np.min(x)
    return dense, dense_offset


# takes a value from V / e-cade (which is what is actually fitted), to mv /
# decade, which is an easier way to report the value in a plot - uxform because
# it is a unit xform function
def uxform_v_per_e_to_mv_per_dec(x):
    return (1e3 / x) * LOGE10


def uxform_log_e_to_log_10(x):
    return x * LOG10E


def reported_versus_fitted_plot(reported_slopes, fitted_slopes,
                                intervals=(0.10, 0.20), fname=None,
                                interactive=False, annotate=None, limit=None):
    # densely sample the range between the reported slopes
    x = np.linspace(np.min(reported_slopes), np.max(reported_slopes))

    # calculate the shading alpha step for the user-provided intervals
    alpha_step = 0.10 / (len(intervals) - 1)

    # now make the figure
    plt.figure()
    plt.plot(reported_slopes, fitted_slopes, 'ko')
    plt.plot(x, x, 'r-')
    for idx, ival in enumerate(intervals):
        alpha = 0.20 - (idx * alpha_step)
        plt.fill_between(x, (1 - ival) * x, (1 + ival) * x, color='r', alpha=alpha)
    plt.fill_between(x, 0.80 * x, 1.20 * x, color='r', alpha=0.10)
    plt.xlabel('Reported Tafel Slope [mV/decade]')
    plt.ylabel('MAP Fitted Tafel Slope [mV/decade]')

    # if this is not None, it should contain the annotation tuples
    if annotate is not None:
        for lab, fitted, reported in annotate:
            plt.annotate(lab, (reported, fitted), textcoords='offset points',
                         xytext=(5, 5), ha='center')

    # set the bounds if asked
    if limit is not None:
        plt.xlim([25, limit])
        plt.ylim([25, limit])

    if fname is not None:
        plt.savefig(fname)

    if interactive:
        plt.show()

    plt.close()


def single_panel_fit_examination_plot(voltages, currents, optimal_model,
                                      fname=None, interactive=False,
                                      offset=True):
    # all model plots will be done on a densely sampled array of voltages, so
    # do the densification here
    d_voltages, d_voltages_offset = densely_sample_array(voltages)

    # evaluate the a posteriori model on the densely sampled voltages
    if offset:
        optimal_model_data = optimal_model(d_voltages_offset)
    else:
        optimal_model_data = optimal_model(d_voltages)

    # Panel 1: plot the raw data and the fitted model
    plt.figure()
    plt.plot(voltages, currents, 'ko', label='Measured Data')
    plt.plot(d_voltages, optimal_model_data, 'r-', label='Fitted Model')
    plt.xlabel('$V_{\mathrm{appl.}}$ [V]')
    plt.ylabel(r'$\log \left[i_{\mathrm{prod.}}\right] + C_{\mathrm{shift}}$')

    if fname is not None:
        plt.savefig(fname)

    if interactive:
        plt.show()

    plt.close()


def three_panel_fit_examination_plot(voltages, currents, trace, ap_model,
                                     reported_tafel=None,
                                     tafel_param_name='alpha',
                                     tafel_unit_xform=uxform_v_per_e_to_mv_per_dec,
                                     ilim_param_name='ilim',
                                     ilim_unit_xform=uxform_log_e_to_log_10,
                                     cutoff_fits=None, fname=None,
                                     interactive=False):
    # all model plots will be done on a densely sampled array of voltages, so
    # do the densification here
    d_voltages, d_voltages_offset = densely_sample_array(voltages)

    # evaluate the a posteriori model on the densely sampled voltages
    ap_model_data = ap_model(d_voltages_offset)

    # Panel 1: plot the raw data and the fitted model
    plt.figure(figsize=(16, 5))
    plt.subplot(1, 3, 1)
    plt.plot(voltages, currents, 'ko', label='Measured Data')
    plt.plot(d_voltages, ap_model_data, 'r-', label='MAP Model')
    plt.xlabel('$V_{\mathrm{appl.}}$ [V]')
    plt.ylabel(r'$\log \left[i_{\mathrm{prod.}}\right] + C_{\mathrm{shift}}$')

    # evaluate the a priori distribution over tafel slopes
    ap_tafels = tafel_unit_xform(trace.get_values(tafel_param_name))

    # Panel 2: plot the a posteriori distribution over the Tafel slope
    plt.subplot(1, 3, 2)
    sns.kdeplot(ap_tafels, shade=True, color='g')
    plt.xlabel(r'$\alpha^{-1}$ [mV/decade]', fontsize=14)
    plt.ylabel(r'$p(\alpha^{-1}|\,\mathrm{data})$', fontsize=14)
    plt.axvline(x=np.mean(ap_tafels), color='g', linestyle='-',
                label='MAP')
    if reported_tafel is not None:
        plt.axvline(x=reported_tafel, color='k', linestyle='-', label='Reported Value')

    # if we had enough points, plot the range of cutoff tafel fits
    if cutoff_fits is not None:
        min_tslope = np.min(cutoff_fits)
        max_tslope = np.max(cutoff_fits)
        plt.axvline(x=min_tslope, color='b', linestyle='-',
                    label='Min Cutoff Fits')
        plt.axvline(x=max_tslope, color='r', linestyle='-',
                    label='Max Cutoff Fits')
    plt.legend()

    # Panel 3: plot the joint distribution over the tafel slope and the
    # limiting current
    ap_ilims = ilim_unit_xform(trace.get_values(ilim_param_name))
    plt.subplot(1, 3, 3)
    sns.kdeplot(ap_tafels, ap_ilims)
    plt.xlabel(r'$\alpha^{-1}$ [mV/decade]')
    plt.ylabel(r'$\log_{10}\left(i_{\mathrm{MT}}\right)$ [mA/$\mathrm{cm}^2$]')
    plt.tight_layout()

    if fname is not None:
        plt.savefig(fname)

    if interactive:
        plt.show()

    plt.close()
