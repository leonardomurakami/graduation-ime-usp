import numpy as np

N = 100
N_ACTORS = list(range(1, N+1))
OPINIONS = [-1, 1]

actor_opinion_history = {actor: [] for actor in N_ACTORS}
full_opinion_history = []
pressure_exerted = [np.random.choice(OPINIONS)*np.random.randint(0, 5) for i in N_ACTORS]
pressure_exerted[0] = 0


def last_agent_opinion_emission(actor):
    return max(actor_opinion_history[actor])


def pressure_exerted_on_actor(actor, current_n):
    pressure = 0
    for timestamp in range(last_agent_opinion_emission(actor), current_n+1):
        pressure += full_opinion_history[timestamp]


def probability_of_opinion_of_actor(current_opinion, current_actor, pressures):
    self_opinion = np.exp(current_opinion*pressures[current_actor-1])
    network_opinion = 0
    for actor in N_ACTORS:
        for opinion in OPINIONS:
            network_opinion += np.exp(opinion*pressures[actor-1])
    return self_opinion/network_opinion


def probability_of_opinion(current_opinion, pressures, n_actors=N_ACTORS, opinions=OPINIONS):
    self_opinions = 0
    network_opinion = 0
    for actor in n_actors:
        self_opinions += np.exp(current_opinion*pressures[actor-1])
        for opinion in opinions:
            network_opinion += np.exp(opinion*pressures[actor-1])
    return self_opinions/network_opinion


def emit_opinion(pressure):
    positive_opinion_probability = probability_of_opinion(1, pressure)
    if np.random.rand() < positive_opinion_probability:
        emitted_opinion = 1
    else:
        emitted_opinion = -1
    return emitted_opinion

def update_pressure(pressure_exerted, actor, opinion):
    for i in range(len(pressure_exerted)):
        if i+1 == actor:
            pressure_exerted[i] = 0
        else:
            pressure_exerted[i] += opinion
    return pressure_exerted

def simulate(time, initial_pressure):
    for n in range(time):
        actor = np.random.choice(N_ACTORS)
        actor_opinion_history[actor] = n
        actor_pressure = initial_pressure[actor-1]
        emitted_opinion = emit_opinion(initial_pressure)
        full_opinion_history.append(emitted_opinion)
        initial_pressure = update_pressure(initial_pressure, actor, emitted_opinion)
        opinion_history = np.array(full_opinion_history)
        print(f"Percentage of positive opinion: {len(opinion_history[opinion_history==1])/len(opinion_history)}% - Emitted Opinion: {emitted_opinion}")
