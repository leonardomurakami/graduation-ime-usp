import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import monte_carlo_methods as mcm
import qng_monte_carlo_methods as qng

from ghalton import Halton

############## CONSTANTS ##############
CPF = 50451412877
RG = 394353985

A_VALUE = RG * 10**-9
B_VALUE = CPF * 10**-11

f_x = lambda x: np.exp(-A_VALUE*x)*np.cos(B_VALUE*x)

def estimate_error(
    monte_carlo_algorithm,
    f_x, 
    n_batches=100, 
    distribution=None,
    control_variate=None,
    gamma_integrated_control_variate=None
  ):
  #to estimate error (given that we do not have the exact value we want to achieve)
  #we will assume that the mean value of num_batches will be the correct value
  #and the error will be calculated as the error of each batch to the mean
  monte_carlo_values = []
  for i in range(n_batches):
    if distribution is not None:
      estimated_value = monte_carlo_algorithm(distribution, f_x)
    elif control_variate is not None and gamma_integrated_control_variate is not None:
      estimated_value = monte_carlo_algorithm(control_variate, gamma_integrated_control_variate, f_x)
    else:
      estimated_value = monte_carlo_algorithm(f_x)
    monte_carlo_values.append(estimated_value)

  approximate_value_mean = np.mean(monte_carlo_values)
  approximate_error = [
    np.abs(value - approximate_value_mean)/approximate_value_mean for value in monte_carlo_values
  ]
  return approximate_error, monte_carlo_values

def compare_methods(method_1, method_2, estimate_error_args={}, figname=None):
    def rolling_average(list):
        average_till_point = []
        for i in range(1, len(list)):
            average_till_point.append(np.mean(list[:i]))
        return average_till_point

    qng_errors_crude, qng_values_crude = estimate_error(method_1, f_x, **estimate_error_args)
    mcm_errors_crude, mcm_values_crude = estimate_error(method_2, f_x, **estimate_error_args)

    qng_plot_list = rolling_average(qng_values_crude)
    mcm_plot_list = rolling_average(mcm_values_crude)
    fig = plt.figure()
    plt.plot(qng_plot_list, label='Quasi-random Number Generator MCM')
    plt.plot(mcm_plot_list, c='red', label='Random MCM')
    plt.legend()
    fig.savefig(figname)

def main():
  compare_methods(qng.crude_monte_carlo, mcm.crude_monte_carlo,  figname='CrudeComparison')

  compare_methods(qng.hit_or_miss_monte_carlo, mcm.hit_or_miss_monte_carlo,  figname='HitOrMissComparison')

  distribution = {"distribution": stats.beta(a=1, b=1.2)}
  compare_methods(qng.importance_sampling_monte_carlo, mcm.importance_sampling_monte_carlo, distribution,  figname='BetaImportanceSamplingComparison')

  distribution = {"distribution": stats.gamma(a=1, scale=1.4)}
  compare_methods(qng.importance_sampling_monte_carlo, mcm.importance_sampling_monte_carlo, distribution,  figname='GammaImportanceSamplingComparison')

  distribution = {"distribution": stats.weibull_min(c=1, scale=1.1)}
  compare_methods(qng.importance_sampling_monte_carlo, mcm.importance_sampling_monte_carlo, distribution,figname='WeibullImportanceSamplingComparison')

  control_variates = {
    "control_variate": lambda x: -0.4*x + 1,
    "gamma_integrated_control_variate": 0.8
  }
  compare_methods(qng.control_variates_monte_carlo, mcm.control_variates_monte_carlo, control_variates, 'ControlVariatesComparison')

if __name__ == '__main__':
  main()