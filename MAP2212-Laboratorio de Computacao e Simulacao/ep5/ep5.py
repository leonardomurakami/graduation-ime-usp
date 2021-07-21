import math
import numpy as np
import random as rd
import time
import scipy.stats as sp

from scipy.special import gamma

class Dirichlet:
  def __init__(self, alpha):
    self._alpha = np.array(alpha)
    self._alpha0 = np.sum(self._alpha)
    self._m = len(alpha)
    self._covariance_matrix = self._calculate_covariance_matrix()
    self._beta_norm = self._multivariate_beta()

  def __calculate_cov(self, i, j):
    return (
      (-self._alpha[i]*self._alpha[j])/
      ((self._alpha0**2)*(self._alpha0 + 1))
    )

  def __calculate_var(self, i):
    return (
      (self._alpha[i]*(self._alpha0 - self._alpha[i]))/
      ((self._alpha0**2)*(self._alpha0 + 1))
    )
    
  def _calculate_covariance_matrix(self):
    covariance_matrix = np.empty(shape=(self._m, self._m))
    for i in range(self._m):
      for j in range(self._m):
        if i != j:
          covariance_matrix[i, j] = self.__calculate_cov(i, j)
        else:
          covariance_matrix[i, j] = self.__calculate_var(i)
    return covariance_matrix

  def pdf(self, x):
    '''Returns pdf value for `x`.'''
    if any([i < 0 for i in x]):
      return 0
    posterior_potential_list = [
      math.pow(xx, aa - 1) for (xx, aa) in zip(x, self._alpha)
    ]
    pdf_x = 1    
    for pp in posterior_potential_list:
      pdf_x *= pp
    return pdf_x/self._beta_norm


  def _multivariate_beta(self):
    beta_top = 1    
    for alpha in self._alpha:
      beta_top*=gamma(alpha)
    return beta_top/gamma(sum(self._alpha))

  def _sample_from_gamma(self, alphas):
    return [rd.gammavariate(alpha, 1) for alpha in alphas]

  @staticmethod
  def _coin_flip(p):
    unif = np.random.uniform(0, 1)
    if unif < p:
      return True
    return False

  def sample_metropolis_hasting(self, num_points):
      current_point = [0.2,0.3,0.5]
      mean = np.array([0,0,0])
      points = [current_point]
      n_current_points = 1
      #burn in
      for _ in range(1000):
        next_point = current_point + sp.multivariate_normal.rvs(mean, self._covariance_matrix)        
        if self._coin_flip(np.min([1, self.pdf(next_point)/self.pdf(current_point)])):
          current_point = next_point
      while n_current_points < num_points:
          next_point = current_point + np.random.multivariate_normal(mean, self._covariance_matrix)           
          if self._coin_flip(np.min([1, (self.pdf(next_point))/self.pdf(current_point)])):
            current_point = next_point
          points.append(current_point)
          n_current_points += 1
      return points



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
    return self._posterior_dist.sample_metropolis_hasting(samples)


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
    if v != -1:
      print(f"U(v) = {sm.U(v)}")

main()

