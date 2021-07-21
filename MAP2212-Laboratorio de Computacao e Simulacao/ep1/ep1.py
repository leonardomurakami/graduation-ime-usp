from random import uniform
from os import system
from statistics import mean, stdev, pstdev
from math import sqrt

CIRCLE_RADIUS = 1
#generate coordinate of x and y
#uniformly distributed between 0 and 1
def get_point():
  x = uniform(CIRCLE_RADIUS, -CIRCLE_RADIUS)
  y = uniform(CIRCLE_RADIUS, -CIRCLE_RADIUS)
  return (x, y)

#computate the vector module of x and y
def vector_module(vector_components):
  count = 0
  partial_sum = 0
  for component in vector_components:
      partial_sum += component**2
      count += 1
  return pow(partial_sum, 1/count)

def calculate_pi(n_samples):
  #generate T utilizing vector module, assigning 1 if inside
  #circle and 0 if not
  #instead of saving values to a list and then getting the number
  #of points inside the circle, we update the sum of T as we go
  #to avoid high memory consumption
  sum_T = 0
  for i in range(n_samples):
      if vector_module(get_point()) <= CIRCLE_RADIUS:
          sum_T+=1
  #calculate proportion given in the exercise
  proportion = (1/n_samples)*sum_T
  #return 
  return proportion*4

def early_stopping(target_error, iteration_m=300):
  n_samples = 1
  percentage_error = 1
  while percentage_error > target_error:
    calculated_pis = [calculate_pi(n_samples) for i in range(iteration_m)]
    std_error = stdev(calculated_pis)/sqrt(iteration_m)
    percentage_error = (std_error/mean(calculated_pis))*100
    print("---------------------------")
    print(f"NUM SAMPLES:\t{n_samples}")
    print(f"STD ERROR:\t{std_error}")
    print(f"PERCENTAGE ERROR:\t{percentage_error}")
    print(f"ESTIMATED AVERAGE PI:\t{mean(calculated_pis)}")
    print("---------------------------")
    n_samples*=10
  return mean(calculated_pis)

def main():
  print(early_stopping(0.05))

main()
input()