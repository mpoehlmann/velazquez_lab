import numpy as np
import pymc3 as pm
import scipy.special

LOG10E = np.log10(np.exp(1))
KT_VOLTAGE = 0.026


def series_resistances_model(v, params, frozen_params):
    alpha, b, ilim = params
    return LOG10E * (b + alpha * v - np.log(ilim + np.exp(alpha * v)))


def series_resistances_model_bayes(v, log_iprod, param_bounds, sigma,
                                   frozen_params):
    alpha_bounds, b_bounds, ilim_bounds = param_bounds

    with pm.Model() as bayes_model:
        # instantiate the Bayes parameters
        alpha = pm.Uniform('alpha', lower=alpha_bounds[0], upper=alpha_bounds[1])
        b = pm.Uniform('b', lower=b_bounds[0], upper=b_bounds[1])
        ilim = pm.Uniform('ilim', lower=ilim_bounds[0], upper=ilim_bounds[1])

        # pack the parameters again to pass to the series resistances model
        params = (alpha, b, ilim)

        # offset the voltages to their minimum value
        voff = v - np.min(v)
        current = series_resistances_model(voff, params, frozen_params)
        # current = np.log10(np.exp(1)) * series_resistances_model(voff, params)
        # current = b + alpha * voff - np.log(imt + np.exp(alpha * voff))
        _ = pm.Normal('obs', current, observed=log_iprod, sigma=sigma)

    return bayes_model


# make a name to index map to make correspondence between bayes model
# and simple model explicit
series_resistances_model_bayes.name_to_index_map = dict(alpha=0, b=1, ilim=2)


def marcus_hush_chidsey_model(v, params, frozen_params):
    lam = params[0]
    eta = v / KT_VOLTAGE

    first_term = np.log(scipy.special.erfc((lam - eta) / (2 * np.sqrt(lam))))
    second_term = np.log(scipy.special.erfc(np.sqrt(lam) / 2))
    return LOG10E * (first_term - second_term)


def marcus_hush_chidsey_model_bayes(v, log_iprod, param_bounds, sigma,
                                    frozen_params):
    lam_bounds = param_bounds[0]

    with pm.Model() as bayes_model:
        # instantiate the Bayes parameters
        lam = pm.Uniform('lam', lower=lam_bounds[0], upper=lam_bounds[1])

        # pack the parameters again to pass to the series resistances model
        params = (lam, )

        # offset the voltages to their minimum value
        voff = v - np.min(v)

        # instantiate the observations variable
        current = marcus_hush_chidsey_model(voff, params)
        _ = pm.Normal('obs', current, observed=log_iprod, sigma=sigma)

    return bayes_model


# make a name to index map to make correspondence between bayes model
# and simple model explicit
marcus_hush_chidsey_model_bayes.name_to_index_map = dict(lam=0)


def heyrovsky_her_model(v, params, frozen_params):
    Kv, Vv0, kh, Vh0, alpha_h = params
    a_proton, a_water = frozen_params

    f = 1 / KT_VOLTAGE
    first_term = np.log(kh) + np.log(Kv) + 2 * np.log(a_proton)
    second_term = -alpha_h * f * (v - Vh0)
    third_term = -np.log(a_water * np.exp(f * (v - Vv0)) + Kv * a_proton)

    return first_term + second_term + third_term


def heyrovsky_her_model_bayes(v, log_iprod, param_bounds, sigma, frozen_params):
    Kv_bounds = param_bounds[0]
    Vv0_bounds = param_bounds[1]
    kh_bounds = param_bounds[2]
    Vh0_bounds = param_bounds[3]
    alpha_h_bounds = param_bounds[4]

    with pm.Model() as bayes_model:
        # instantiate the Bayes parameters
        Kv = pm.Uniform('Kv', lower=Kv_bounds[0], upper=Kv_bounds[1])
        Vv0 = pm.Uniform('Vv0', lower=Vv0_bounds[0], upper=Vv0_bounds[1])
        kh = pm.Uniform('kh', lower=kh_bounds[0], upper=kh_bounds[1])
        Vh0 = pm.Uniform('Vh0', lower=Vh0_bounds[0], upper=Vh0_bounds[1])
        alpha_h = pm.Uniform('alpha_h', lower=alpha_h_bounds[0],
                             upper=alpha_h_bounds[1])

        # pack the parameters again to pass to the series resistances model
        params = (Kv, Vv0, kh, Vh0, alpha_h)

        # instantiate the observations variable
        current = heyrovsky_her_model(v, params, frozen_params)
        _ = pm.Normal('obs', current, observed=log_iprod, sigma=sigma)

    return bayes_model


# make a name to index map to make correspondence between bayes model
# and simple model explicit
heyrovsky_her_model_bayes.name_to_index_map = dict(Kv=0, Vv0=1, kh=2, Vh0=3,
                                                   alpha_h=4)


def bicarbonate_1_model(inputs, params):
    l_k1fhco3, l_k1fh2o, b1hco3, b1h2o, l_Khco3, gam = params
    cco2, chco3, v = inputs

    f = 1 / KT_VOLTAGE

    num_term_1 = np.exp(l_k1fhco3) * cco2 * chco3 * np.exp(-b1hco3 * f * v)
    num_term_2 = np.exp(l_k1fh2o) * cco2 * np.exp(-b1h2o * f * v)
    num = num_term_1 + num_term_2
    denom = 1 + np.exp(l_Khco3) * chco3 * np.exp(gam * f * v)

    return num / denom


def bicarbonate_1_model_bayes(v, log_iprod, param_bounds, sigma, frozen_params):
    Kv_bounds = param_bounds[0]
    Vv0_bounds = param_bounds[1]
    kh_bounds = param_bounds[2]
    Vh0_bounds = param_bounds[3]
    alpha_h_bounds = param_bounds[4]

    with pm.Model() as bayes_model:
        # instantiate the Bayes parameters
        Kv = pm.Uniform('Kv', lower=Kv_bounds[0], upper=Kv_bounds[1])
        Vv0 = pm.Uniform('Vv0', lower=Vv0_bounds[0], upper=Vv0_bounds[1])
        kh = pm.Uniform('kh', lower=kh_bounds[0], upper=kh_bounds[1])
        Vh0 = pm.Uniform('Vh0', lower=Vh0_bounds[0], upper=Vh0_bounds[1])
        alpha_h = pm.Uniform('alpha_h', lower=alpha_h_bounds[0],
                             upper=alpha_h_bounds[1])

        # pack the parameters again to pass to the series resistances model
        params = (Kv, Vv0, kh, Vh0, alpha_h)

        # instantiate the observations variable
        current = heyrovsky_her_model(v, params, frozen_params)
        _ = pm.Normal('obs', current, observed=log_iprod, sigma=sigma)

    return bayes_model


# make a name to index map to make correspondence between bayes model
# and simple model explicit
heyrovsky_her_model_bayes.name_to_index_map = dict(Kv=0, Vv0=1, kh=2, Vh0=3,
                                                   alpha_h=4)
