import imageio
import os

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

N = 50
N_ACTORS = list(range(1, N+1))
OPINIONS = [-1, 1]
POLARIZATION_PARAM = np.log(2)

actor_opinion_history = {actor: [] for actor in N_ACTORS}
full_opinion_history = []

#pressure_exerted = [np.random.choice(OPINIONS)*np.random.randint(0, 5) for i in N_ACTORS]
pressure_exerted = [0 for i in N_ACTORS]

    
def last_agent_opinion_emission(actor):
    return max(actor_opinion_history[actor])


def pressure_exerted_at_n(actor, current_n):
    pressure = 0
    for timestamp in range(last_agent_opinion_emission(actor), current_n+1):
        pressure += full_opinion_history[timestamp]


def probability_of_opinion_of_actor(
    current_opinion: int, 
    current_actor: int, 
    pressures: list, 
    polarization_param: int=POLARIZATION_PARAM, 
    n_actors: int=N_ACTORS, 
    opinions: list=OPINIONS
):
    self_opinion = np.exp(polarization_param*current_opinion*pressures[current_actor-1])
    network_opinion = 0
    for actor in n_actors:
        for opinion in opinions:
            network_opinion += np.exp(polarization_param*opinion*pressures[actor-1])
    return self_opinion/network_opinion


def probability_of_opinion(
    current_opinion: int, 
    pressures: list, 
    polarization_param: int=POLARIZATION_PARAM, 
    n_actors: int=N_ACTORS, 
    opinions: list=OPINIONS
):
    self_opinion = 0
    network_opinion = 0
    for actor in n_actors:
        self_opinion += np.exp(polarization_param*current_opinion*pressures[actor-1])
        for opinion in opinions:
            network_opinion += np.exp(polarization_param*opinion*pressures[actor-1])
    return self_opinion/network_opinion


def update_pressure(pressure, actor, opinion):
    for i in range(len(pressure)):
        if i+1 == actor:
            pressure[i] = 0
        else:
            pressure[i] += opinion
    return pressure


def emit_opinion(pressure):
    positive_opinion_probability = probability_of_opinion(1, pressure)
    if np.random.rand() < positive_opinion_probability:
        emitted_opinion = 1
    else:
        emitted_opinion = -1
    return emitted_opinion


def actor_probability(pressure, actor, n_actors=N_ACTORS, opinions=OPINIONS):
    self_prob = np.exp(pressure[actor-1]) + np.exp(-pressure[actor-1])
    network_prob = 0
    for actor in n_actors:
        for opinion in opinions:
            network_prob += np.exp(pressure[actor-1]*opinion)
    return self_prob/network_prob


def calculate_actors_probabilities(pressure, n_actors=N_ACTORS):
    return [actor_probability(pressure, actor) for actor in n_actors]


def create_plot(pressure, n):
    plt.figure()
    x_plt = np.array(N_ACTORS)
    y_plt = np.array(pressure)
    mask1 = y_plt < 0
    mask2 = y_plt > 0
    ax = plt.bar(x=x_plt[mask1], height=y_plt[mask1], width=0.3, color='red')
    ax = plt.bar(x=x_plt[mask2], height=y_plt[mask2], width=0.3, color='blue')
    plt.ylim(-50, 50)
    plt.savefig(f'./plots/pressure_polarization_{n}.png')
    plt.close()


def create_gif(fig_prefix, size):   
    with imageio.get_writer('pressure.gif', mode='I') as writer:
        for filenumber in range(size):
            file_path = f"{fig_prefix}_{filenumber}.png"
            image = imageio.imread(file_path)
            writer.append_data(image)
            os.remove(file_path)


def find_probability_of_v_given_u(pressure_u, pressure_v, opinions=OPINIONS, verbose=False):
    n_actors = list(range(1, len(pressure_v)+1))
    for actor in n_actors:
        for opinion in opinions:
            pressure_u_copy = pressure_u.copy()
            if update_pressure(pressure_u_copy, actor, opinion) == pressure_v:
                if verbose:
                    print("p(v|u) > 0")
                    print(f"Actor: {actor}")
                    print(f"With opinion: {opinion}")
                return probability_of_opinion_of_actor(opinion, actor, pressure_u, n_actors=n_actors)
    if verbose:
        print("p(v|u) = 0")
    return None

def find_probability_of_v_given_u_multiple_steps(
    pressure_u, 
    pressure_v, 
    max_depth, 
    depth=0, 
    opinions=OPINIONS, 
    verbose=False
):
    n_actors = list(range(1, len(pressure_v)+1))
    found=False
    probability = 0
    for actor in n_actors:
        for opinion in opinions:
            pressure_u_copy = pressure_u.copy()
            if depth < max_depth:
                probability, found = find_probability_of_v_given_u_multiple_steps(
                    update_pressure(pressure_u_copy, actor, opinion),
                    pressure_v, max_depth, depth=depth+1,
                    opinions=opinions, verbose=verbose
                )
            pressure_u_copy = pressure_u.copy()
            if (updated_u := update_pressure(pressure_u_copy, actor, opinion)) == pressure_v or found:
                if verbose:
                    print(f"Depth {depth}, Actor: {actor}, Opinion: {opinion}, Pressures: {updated_u}, P(U_{depth} | U_{depth+1}): {probability}")
                return probability_of_opinion_of_actor(opinion, actor, pressure_u, n_actors=n_actors), True
    return None, False


def simulate(time, pressure):
    for n in range(time):
        actor_probabilities = calculate_actors_probabilities(pressure, N_ACTORS)
        actor = np.random.choice(N_ACTORS, p=actor_probabilities)
        actor_opinion_history[actor] = n
        actor_pressure = pressure[actor-1]

        emitted_opinion = emit_opinion(pressure)

        full_opinion_history.append(emitted_opinion)
        pressure = update_pressure(pressure, actor, emitted_opinion)
        opinion_history = np.array(full_opinion_history)

        print(f"Percentage of positive opinion: {len(opinion_history[opinion_history==1])/len(opinion_history)}% - Emitted Opinion: {emitted_opinion}")


def simulate_with_gif(time, pressure):
    for n in range(time):
        actor_probabilities = calculate_actors_probabilities(pressure, N_ACTORS)
        actor = np.random.choice(N_ACTORS, p=actor_probabilities)
        actor_opinion_history[actor] = n
        actor_pressure = pressure[actor-1]

        emitted_opinion = emit_opinion(pressure)

        full_opinion_history.append(emitted_opinion)
        pressure = update_pressure(pressure, actor, emitted_opinion)
        opinion_history = np.array(full_opinion_history)

        print(f"Percentage of positive opinion: {len(opinion_history[opinion_history==1])/len(opinion_history)}% - Emitted Opinion: {emitted_opinion}")
        create_plot(pressure, n)
    create_gif('./plots/pressure_polarization', time)