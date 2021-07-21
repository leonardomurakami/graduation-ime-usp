from tqdm import tqdm
import numpy as np
import imageio
import os
import matplotlib.pyplot as plt

class SimpleExtremeChangeModel:
    def __init__(self, n_max, llambda, opinions=[-1, 1]):
        self._n_max = n_max
        self._opinions = opinions
        self._lambda = llambda
        self._z_n = [i for i in range(-self._n_max, self._n_max+1)]
        #lambda > 0 empurra s_n para as extremidades
        #lambda = 0 torna a simulacao um passeio aleatorio
        #lambda < 0 empurra a simulacao para o ponto central 0

    @staticmethod
    def signal(z):
        if z > 0:
            return 1
        elif z < 0:
            return -1
        return 0


    def _time_step(self, s_n):
        opinion = np.random.choice(self._opinions)
        proba = self.probability_of_opinion(s_n, opinion)
        if np.random.uniform() < proba:
            s_n = self.update_opinion(s_n, opinion)
        else:
            s_n = self.update_opinion(s_n, -opinion)
        return s_n


    def probability_of_opinion(self, s_n, opinion):
        return (
            np.exp(self._lambda*opinion*self.signal(s_n))/(
                np.exp(self._lambda*self.signal(s_n)) + 
                np.exp(-self._lambda*self.signal(s_n))
            )
        )

    def update_opinion(self, s_n, opinion):
        new_s = s_n + opinion
        if new_s > self._n_max:
            return self._n_max
        elif new_s < -self._n_max:
            return -self._n_max
        return new_s

    
    def pressure(self):
        large_number = 1000000
        s_n_space = self.generate_s_n_space(large_number)
        return np.mean(s_n_space)
    
    
    def generate_s_n_space(self, time):
        s_n_space = []
        s_n = np.random.choice(self._z_n)
        for _ in tqdm(range(time)):
            s_n = self._time_step(s_n)
            s_n_space.append(s_n)
        return s_n_space


    def simulate(self, time, initial_s_n=None):
        s_n = (
            np.random.choice(self._z_n) 
            if initial_s_n is None 
            else initial_s_n
        )
        print(f"Initial s_n: {s_n}")
        for _ in range(time):
            s_n = self._time_step(s_n)
            print(f"S_{_}: {s_n}")
    
    def time_to_hit(self, z, iterations=50):
        time_to_hit = []
        print(f"Running {iterations} iterations...")
        for _ in tqdm(range(iterations)):
            time = 1
            s_n = z
            s_n = self._time_step(s_n)
            while s_n != z and time < 50000:
                s_n = self._time_step(s_n)
                time += 1
            time_to_hit.append(time)
        return np.mean(time_to_hit)
    
    def time_proportion(self, time):
        time_spent = {z: 0 for z in self._z_n}
        s_n = np.random.choice(self._z_n)
        for _ in range(time):
            s_n = self._time_step(s_n)
            time_spent[s_n] += 1
        return time_spent
    
    def invariant_probability_of_zero(self):
        return (
            1/(
                1 + ((np.exp(self._lambda) + np.exp(-self._lambda))*
                sum([np.exp(self._lambda*((2*(z-1)) + 1)) for z in range(1, self._n_max+1)]))
            )
        )

    def invariant_probability(self, z):
        return (
            0.5*self.invariant_probability_of_zero()*
            (np.exp(-self._lambda) + np.exp(self._lambda))*
            np.exp(self._lambda*((2*(z-1))+1))
        )

    def time_proportion_gif(self, time):
        time_spent = {z: 0 for z in self._z_n}
        s_n = np.random.choice(self._z_n)
        for i in range(time):
            s_n = self._time_step(s_n)
            time_spent[s_n] += 1
            self.plot_graph(time_spent, i)
        self.create_gif('./plots/sec_model', time)
        return time_spent

    @staticmethod
    def plot_graph(time_spent, i):
        y = np.array(list(time_spent.values()))/(i+1)
        plt.figure()
        plt.ylim(0, 1)
        plt.bar(x=time_spent.keys(), height=y)
        plt.savefig(f'./plots/sec_model_{i}.png')
        plt.close()

    @staticmethod
    def create_gif(fig_prefix, size):   
        with imageio.get_writer('extreme_change.gif', mode='I') as writer:
            for filenumber in range(size):
                file_path = f"{fig_prefix}_{filenumber}.png"
                image = imageio.imread(file_path)
                writer.append_data(image)
                os.remove(file_path)
