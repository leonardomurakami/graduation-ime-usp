#Leonardo Heidi Almeida Murakami
import numpy as np
import scipy.stats as stats

############## CONSTANTS ##############
CPF = ['REDACTED']
RG = ['REDACTED']

A_VALUE = RG * 10**-9
B_VALUE = CPF * 10**-11

N_CRUDE = 300000
N_HIT_OR_MISS = 400000
N_IMPORTANCE_SAMPLING = 25000
N_CONTROL_VARIATE = 1000
M_SAMPLES = 100

f_x = lambda x: np.exp(-A_VALUE*x)*np.cos(B_VALUE*x)


############## UTILS ##############
def generate_point():
  random_x_coordinate = np.random.uniform(low=0, high=1)
  random_y_coordinate = np.random.uniform(low=0, high=1)
  return (random_x_coordinate, random_y_coordinate)

def generate_values(dist, size=30000):
  random_values = dist.rvs(size=size)
  return random_values[random_values < 1]

############## CRUDE MONTE CARLO ##############
def crude_monte_carlo(f_x, n_samples=N_CRUDE):
  #to avoid using too much memory (to allow testing high N numbers)
  #were going to update the result iteratively
  approximate_value = 0
  for i in range(n_samples):
    random_value = np.random.uniform(low=0, high=1)
    approximate_value = (approximate_value*i + f_x(random_value))/(i+1)
  return approximate_value

############## HIT OR MISS MONTE CARLO ##############
def hit_or_miss_monte_carlo(f_x, n_samples=N_HIT_OR_MISS):
  #to avoid using too much memory (to allow testing high N numbers)
  #were going to update the result iteratively
  points_under_curve = 0
  for i in range(n_samples):
    generated_x, generated_y = generate_point()
    curve_y = f_x(generated_x)
    if curve_y >= generated_y:
      points_under_curve += 1
  return points_under_curve/n_samples

############## IMPORTANCE SAMPLING MONTE CARLO ##############
def importance_sampling_monte_carlo(distribution, f_x, n_samples=N_IMPORTANCE_SAMPLING):
  #instead of avoiding using too much memory, in this case we are going to
  #generate all f_x and distribution samples at once, since scipy
  #is kind of slow and will take too long if we genrate the estimate iteratively
  #random_values = distribution.rvs(size=n_samples)
  random_values = generate_values(distribution, size=n_samples)
  #pre calculate f_x values and dist pdf
  distribution_pdf_values = distribution.pdf(random_values)
  f_x_values = list(map(f_x, random_values))
  approximate_value = np.sum(np.array(f_x_values)/np.array(distribution_pdf_values))/n_samples
  return approximate_value

############## CONTROL VARIATES MONTE CARLO ##############
def control_variates_monte_carlo(control_variate, gamma_integrated_control_variate, f_x, n_samples=N_CONTROL_VARIATE):
  #to avoid using too much memory (to allow testing high N numbers)
  #were going to update the result iteratively
  approximate_value = 0
  for i in range(n_samples):
    random_value = np.random.uniform(low=0, high=1)
    approximate_value = (approximate_value*i + (f_x(random_value)-control_variate(random_value)+gamma_integrated_control_variate))/(i+1)
  return approximate_value


def estimate_error(
    monte_carlo_algorithm, 
    f_x, 
    n_batches=M_SAMPLES, 
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
  return approximate_error, approximate_value_mean



def main():
  errors_crude, estimated_value_crude = estimate_error(crude_monte_carlo, f_x)
  print("-"*4 + "CRUDE MONTE CARLO" + "-"*4)
  print(f"Mean Error: \t {np.mean(errors_crude)}")
  print(f"Estimated Value: \t {estimated_value_crude}")

  errors_hom, estimated_value_hom = estimate_error(hit_or_miss_monte_carlo, f_x)
  print("-"*4 + "HIT OR MISS MONTE CARLO" + "-"*4)
  print(f"Mean Error: \t {np.mean(errors_hom)}")
  print(f"Estimated Value: \t {estimated_value_hom}")

  isc_errors, isc_estimated_value = estimate_error(importance_sampling_monte_carlo, f_x, distribution=stats.beta(a=1, b=1.2))
  print("-"*4 + "BETA DISTRIBUTION IMPORTANCE SAMPLING MONTE CARLO" + "-"*4)
  print(f"Mean Error: \t {np.mean(isc_errors)}")
  print(f"Estimated Value: \t {isc_estimated_value}")

  isc_errors, isc_estimated_value = estimate_error(importance_sampling_monte_carlo, f_x, distribution=stats.gamma(a=1, scale=1.4))
  print("-"*4 + "GAMMA DISTRIBUTION IMPORTANCE SAMPLING MONTE CARLO" + "-"*4)
  print(f"Mean Error: \t {np.mean(isc_errors)}")
  print(f"Estimated Value: \t {isc_estimated_value}")

  isc_errors, isc_estimated_value = estimate_error(importance_sampling_monte_carlo, f_x, distribution=stats.weibull_min(c=1, scale=1.1))
  print("-"*4 + "WEIBULL DISTRIBUTION IMPORTANCE SAMPLING MONTE CARLO" + "-"*4)
  print(f"Mean Error: \t {np.mean(isc_errors)}")
  print(f"Estimated Value: \t {isc_estimated_value}")
  
  control_variate = lambda x: -0.4*x + 1
  gamma_integrated_control_variate = 0.8
  control_variate_errors, control_variate_estimated_value = estimate_error(
      control_variates_monte_carlo, f_x, 
      control_variate = control_variate,
      gamma_integrated_control_variate = gamma_integrated_control_variate
      )
  print("-"*4 + "CONTROL VARIATES MONTE CARLO" + "-"*4)
  print(f"Mean Error: \t {np.mean(control_variate_errors)}")
  print(f"Estimated Value: \t {control_variate_estimated_value}")
main()