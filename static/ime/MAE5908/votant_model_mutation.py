import os
import imageio

import numpy as np
import matplotlib.pyplot as plt

N = 100
N_ACTORS = [i for i in range(1, N+1)]
OPINIONS = [-1, 1]
ACTORS_STARTING_OPINIONS = [np.random.choice(OPINIONS) for _ in range(N)]
INFLUENCE = {i+1: N_ACTORS[:i] + N_ACTORS[i+1:] for i in range(len(N_ACTORS))}
MUTATION_PROBABILITY = 0.2
EPSILON = 1 - MUTATION_PROBABILITY

def create_plot(opinions, n, n_actors=N_ACTORS):
    plt.figure()
    x_plt = np.array(list(range(1, len(n_actors)+1)))
    y_plt = np.array(opinions)
    mask1 = y_plt < 0
    mask2 = y_plt > 0
    ax = plt.bar(x=x_plt[mask1], height=y_plt[mask1], width=0.3, color='red')
    ax = plt.bar(x=x_plt[mask2], height=y_plt[mask2], width=0.3, color='blue')
    plt.ylim(-2, 2)
    plt.title(f"Iteration {n}")
    plt.savefig(f'./plots/votant_model_{n}.png')
    plt.close()


def create_gif(fig_prefix, size):
    with imageio.get_writer('votant.gif', mode='I') as writer:
        for filenumber in range(size):
            file_path = f"{fig_prefix}_{filenumber}.png"
            image = imageio.imread(file_path)
            writer.append_data(image)
            os.remove(file_path)


def simulate(time, n_actors=N_ACTORS, opinions=OPINIONS, starting_opinions=ACTORS_STARTING_OPINIONS, influence=INFLUENCE):
    for n in range(time):
        mutation = np.random.choice(opinions, p=[1-EPSILON, EPSILON])
        actor = np.random.choice(n_actors)
        influencer = np.random.choice(influence[actor])
        starting_opinions[actor-1] = starting_opinions[influencer-1]*mutation
        create_plot(starting_opinions, n, n_actors=n_actors)
    create_gif('./plots/votant_model', time)

