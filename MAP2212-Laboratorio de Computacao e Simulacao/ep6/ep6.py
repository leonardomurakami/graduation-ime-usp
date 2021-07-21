import math
import numpy as np

from scipy.special import gamma

class Dirichlet:
  def __init__(self, alpha):
    self._alpha = np.array(alpha)
    self._m = len(alpha)


  def pdf(self, x):
    '''Returns pdf value for `x`.'''
    posterior_potential_list = [
      math.pow(xx, aa - 1) for (xx, aa) in zip(x, self._alpha)
    ]
    pdf_x = 1    
    for pp in posterior_potential_list:
      pdf_x *= pp
    b_a = self._multivariate_beta()
    return pdf_x/b_a

  def _multivariate_beta(self):
    beta_top = 1    
    for alpha in self._alpha:
      beta_top*=gamma(alpha)
    return beta_top/gamma(sum(self._alpha))

  def _sample_from_gamma(self, alphas, samples):
    return [np.random.gamma(alpha, size=samples) for alpha in alphas]


  def samples(self, samples):
    # based on 
    # https://eliezersilva.blog/2016/03/13/sampling-from-dirichlet-distribution-using-gamma-distributed-samples/
    gamma_samples = np.array(self._sample_from_gamma(self._alpha, samples))
    return [gamma_samples[:, i] / np.sum(gamma_samples[:, i]) for i in range(samples)]


class StatisticalModel:
  def __init__(
      self, 
      observations: list, 
      prior: list, 
      cut_off_points: int, 
      theta_n_size: int=30000,
  ):
    """[summary]

    Args:
        observations (list): x defined in ep, list of observations
        prior (list): y defined in ep, list of priors
        cut_off_points (int): v defined in ep, number of cut off points 
        theta_n_size (int, optional): Theta space size. Defaults to 30000.
        percentual_weight_adjustment (float, optional): (fraction(v(n-1), v(n)-(1/K))/(1/K)). Defaults to 0.02.
    """
    #data validation
    assert len(observations) == len(prior), "Observations and Prior should have same dimension"
    assert cut_off_points >= 2, "Should have at least 2 cut off points to form a function"
    #data attribution
    self._x = observations
    self._y = prior
    self._k_cut_off_points = cut_off_points
    #startup attributes calculation
    #distribution attributes
    self._dirichlet_alpha = np.array(self._x) + np.array(self._y)
    self._posterior_dist = Dirichlet(self._dirichlet_alpha)
    #theta space attributes
    self._theta_space = self._generate_theta_points(theta_n_size)
    self._f_theta_space = np.array(list(map(self._f, self._theta_space)))
    self._sup_f_theta = max(self._f_theta_space)
    #cut off points attributes
    #attributes to dynamically adjust bins weights to approx 1/K
    self._adjust_bounds_for_balanced_bins()


  def _f(self, theta):
    #call distributions potential distribution function as f
    return self._posterior_dist.pdf(theta)


  def _generate_theta_points(self, samples):
    #generate n points by calling the posterior dist (Dirichlet class)
    #sample function n times
    return self._posterior_dist.samples(samples)


  def _s(self, theta):
    return self._f(theta)/

  def _calculate_fraction_of_cut_off_set(self, lower_bound, upper_bound):
    #calculate fraction through numpy where logic
    subsetter = np.where(np.logical_and(lower_bound <= self._f_theta_space, self._f_theta_space < upper_bound))
    return len(self._f_theta_space[subsetter])/len(self._f_theta_space)


  def _adjust_bounds_for_balanced_bins(self):
    sorted_f_theta = np.sort(self._f_theta_space)
    splitted_bins = np.array_split(sorted_f_theta, self._k_cut_off_points-1)
    self._cut_off_points = [0]
    for bin in splitted_bins:
      self._cut_off_points.append(bin[-1])
    self._cut_off_points[-1] = self._sup_f_theta
    self._fractions = self.calculate_fraction_of_sets()


  def calculate_fraction_of_sets(self):
    previous_v = 0
    fractions = {}
    for v in range(len(self._cut_off_points)):
      previous_f_theta = self._cut_off_points[previous_v]
      current_f_theta = self._cut_off_points[v]
      fractions[f"{previous_f_theta}-{current_f_theta}"] = self._calculate_fraction_of_cut_off_set(previous_f_theta, current_f_theta)
      previous_v = v
    return fractions


  def U(self, v):
    u_v = 0
    if v > self._cut_off_points[-1]:
      return 1
    for current_v, fraction in zip(self._cut_off_points, list(self._fractions.values())):
      if v >= current_v:
        u_v += fraction
      else:
        break
    return u_v
        

  def print_class_attributes(self):
    #debugging function, shows all "printable" 
    #class attributes (or a sample of a attribute)
    print(f"Observations: {self._x}")
    print(f"Prior: {self._y}")
    print(f"Num of cut off points: {self._k_cut_off_points}")
    print(f"Dirichlet Alpha: {self._dirichlet_alpha}")
    print(f"Superior f(theta): {self._sup_f_theta}")
    print(f"Theta Space Sample ([0]): {self._theta_space[0]}")
    print(f"f(Theta) Space Sample ([0]): {self._f_theta_space[0]}")
    print(f"Cut off points Sample ([0]): {self._cut_off_points[0]}")

def main():
  x = list(map(int, input("Valores do vetor X separados por virgula (ex: 4,6,4): ").split(',')))
  y = list(map(int, input("Valores do vetor Y separados por virgula (ex: 1,2,3): ").split(',')))
  v = 0
  k = 50000
  n = 300000
  print("Gerando modelo estatistico, por favor aguarde...")
  start = time.time()
  sm = StatisticalModel(
      observations = x,
      prior = y,
      cut_off_points = k,
      theta_n_size = n
  )
  end = time.time()
  print(f"Time elapsed: {end-start}s")
  print("Insira os valores de v para calcular (insira -1 para encerrar o programa)")
  while v != -1:  
    v = float(input("v: "))
    print(f"U(v) = {sm.U(v)}")

main()
