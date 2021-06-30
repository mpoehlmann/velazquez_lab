import numpy as np
import scipy.optimize
import pymc3 as pm


def sqsum(x):
    return np.sum(np.power(x, 2))


def fit_linear(x, y):
    X = np.vander(x, 2)
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    params = np.einsum('ik,i,ji,j', Vt, 1.0 / S, U, y)
    m, b = params
    return m, b, X


def fit_linear_windowed(x, y, left_window=0, right_window=None):
    # window the data as requested
    if right_window is not None:
        windowed_x = x[left_window:right_window]
        windowed_y = y[left_window:right_window]
    else:
        windowed_x = x[left_window:]
        windowed_y = y[left_window:]

    return fit_linear(windowed_x, windowed_y)


def fit_several_windowed_linear_models(voltages, log_current, rightmost_point):
    windowed_slopes = []
    for rw_bound in range(2, 5):
        tslope, _, _ = fit_linear_windowed(voltages, log_current,
                                           right_window=rw_bound)
        windowed_slopes.append(tslope)

    return windowed_slopes


def fit_nonlinear_with_random_restarts(voltages, log_current, model,
                                       frozen_params, guess=None, nparams=None,
                                       max_restarts=100, verbose=True):
    # offset the voltages
    voff = voltages - np.min(voltages)

    # define a loss function for the fit
    def loss(params):
        resid = log_current - model(voff, params, frozen_params)
        return sqsum(resid)

    # try once with the guess if provided
    if guess is not None:
        result = scipy.optimize.minimize(loss, guess)
        nparams = len(guess)
    else:
        if nparams is None:
            raise ValueError('if not providing a guess, then need to specify '
                             'the number of parameters for the model with '
                             'nparams=N')
        rand_guess = np.abs(np.random.randn(nparams))
        result = scipy.optimize.minimize(loss, rand_guess)

    # if it's not a success, try again with random initial guesses
    restart_counter = 0
    choked = False
    while not result.success:
        rand_guess = np.abs(np.random.randn(nparams))
        result = scipy.optimize.minimize(loss, rand_guess)
        restart_counter += 1

        if restart_counter == max_restarts:
            if verbose:
                print('couldn''t find a fit after %d random restarts' %
                      max_restarts)
                choked = True
            break

    if verbose and not choked:
        print('found fit after %d random restarts' % restart_counter)

    # return a function that evaluates the fitted model, as well as the
    # parameters from the fit
    pstar = result.x
    fitted_model = lambda v: model(v, pstar, frozen_params)

    return pstar, fitted_model


def fit_bayes_with_preconditioned_bounds(voltages, log_current, simple_model,
                                         bayes_model, sigma, frozen_params,
                                         guess=None, nparams=None,
                                         nsamples=1000, param_bounds=None,
                                         nretries=5):
    # first run a regular (non-Bayes) fit to set up the parameter bounds
    pstar, _ = fit_nonlinear_with_random_restarts(voltages, log_current,
                                                  simple_model, frozen_params,
                                                  guess=guess, nparams=nparams)

    # generate a list of parameter bounds for the Bayes fit from the initial
    # fit, naively let's say multiply the optimal model parameters by 10 and go
    # from zero to there - i'm assuming that none of the parameters will ever
    # be negative in a sensible model
    if param_bounds is None:
        param_bounds = [[0, p * 10] for p in pstar]

    # construct the probabilistic model
    prob_model = bayes_model(voltages, log_current, param_bounds, sigma,
                             frozen_params)

    # surround sampling statement with some retrying logic because sometimes
    # the sampling fails
    success = False
    retries = 0
    while retries < nretries and not success:
        with prob_model:
            try:
                trace = pm.sample(nsamples, tune=2000, target_accept=0.90)
                success = True
            except pm.parallel_sampling.ParallelSamplingError:
                print('sampling choked on try %d' % (retries + 1))
                success = False
                retries += 1

    if success:
        return trace
    else:
        return None


def fit_bayes_with_preconditioned_bounds_tweakable(voltages, log_current,
                                                   simple_model, bayes_model,
                                                   sigma, frozen_params,
                                                   guess=None, nparams=None,
                                                   nsamples=1000,
                                                   param_bounds=None,
                                                   nretries=5, top_fac=10):
    # first run a regular (non-Bayes) fit to set up the parameter bounds
    pstar, _ = fit_nonlinear_with_random_restarts(voltages, log_current,
                                                  simple_model, frozen_params,
                                                  guess=guess, nparams=nparams)

    # generate a list of parameter bounds for the Bayes fit from the initial
    # fit, naively let's say multiply the optimal model parameters by 10 and go
    # from zero to there - i'm assuming that none of the parameters will ever
    # be negative in a sensible model
    if param_bounds is None:
        param_bounds = [[0, p * 10] for p in pstar]

    # construct the probabilistic model
    prob_model = bayes_model(voltages, log_current, param_bounds, sigma,
                             frozen_params)

    # surround sampling statement with some retrying logic because sometimes
    # the sampling fails
    success = False
    retries = 0
    while retries < nretries and not success:
        with prob_model:
            try:
                trace = pm.sample(nsamples)
                success = True
            except pm.parallel_sampling.ParallelSamplingError:
                print('sampling choked on try %d' % (retries + 1))
                success = False
                retries += 1

    if success:
        return trace
    else:
        return None


def collapsed_simple_model_from_bayes_model(bayes_trace, simple_model,
                                            frozen_params, name_to_index_map,
                                            trace_func=np.mean):
    # construct an a posteriori model from the parameter traces
    params = np.zeros(len(name_to_index_map))
    for pname, pindex in name_to_index_map.items():
        params[pindex] = np.mean(bayes_trace.get_values(pname))

    print(params)

    ap_model = lambda v: simple_model(v, params, frozen_params)
    return ap_model
