import numpy as np
from math import comb
class RandomBlocksModel:
    def __init__(
        self,
        first_community_members,
        second_community_members,
        conn_matrix=None, 
        num_vertices=None,
        probability_of_connection=None,
    ):
        self._first_community_members = first_community_members
        self._second_community_members = second_community_members
        self.connection_matrix = (
            np.array(conn_matrix)
            if conn_matrix is not None 
            else self._populate_conn_matrix()
        )
        self._num_vertices = (
            num_vertices 
            if conn_matrix is None 
            else len(conn_matrix)
        )
        self.p = (
            probability_of_connection 
            if conn_matrix is None 
            else self.estimate_ps()
        )
        self._p_community1 = self.p[0]
        self._p_community1_2 = self.p[1]
        self._p_community2 = self.p[2]

    def __coin_flip(self, proba):
        unif = np.random.uniform()
        return unif < proba

    def _populate_conn_matrix(self):
        #slide 17 aula 18
        matrix = np.empty(
            shape=(self._num_vertices, self._num_vertices),
            dtype=int
        )
        for i in range(self._num_vertices):
            for j in range(i, self._num_vertices):
                if i == j:
                    matrix[i, j] = 0
                elif (
                    i+1 in self._first_community_members and 
                    j+1 in self._first_community_members
                ):
                    matrix[i, j] = self.__coin_flip(self.p_community1)
                elif (
                    i+1 in self._second_community_members and 
                    j+1 in self._secondfirst_community_members
                ):
                    matrix[i, j] = self.__coin_flip(self.p_community2)
                else:
                    matrix[i, j] = self.__coin_flip(self._p_community1_2)
        for j in range(self._num_vertices):
            for i in range(j, self._num_vertices):
                matrix[i, j] = matrix[j, i]
        return matrix

    def get_only_community_members_subset(self, i, j):
        matrix = self.connection_matrix.copy()
        for x in range(self._num_vertices):
            for y in range(self._num_vertices):
                if (
                    (x+1 not in i or y+1 not in j)
                    and
                    (x+1 not in j or y+1 not in i) 
                ):
                    matrix[x, y] = 5
                elif x == y:
                    matrix[x, y] = 5
        return matrix

    def N_g(self, matrix, value):
        if value == 1:
            return np.count_nonzero(matrix == 1)/2
        elif value == 0:
            return np.count_nonzero(matrix == 0)/2
    
    def log_likelihood(self):
        #probabilidade conjunta do grafo G(N, p) ser exatamente M
        #chamada de verossimilhanca
        subsets = [
            (self._first_community_members, self._first_community_members, self._p_community1), 
            (self._first_community_members, self._second_community_members, self._p_community1_2), 
            (self._second_community_members, self._second_community_members, self._p_community2), 
        ]
        partial_log_likelihood = []
        for subset_i, subset_j, probas in subsets:
            matrix = self.get_only_community_members_subset(subset_i, subset_j)
            partial_log_likelihood.append(self.N_g(matrix, 1)*np.log(probas) + self.N_g(matrix, 0)*np.log(1-probas))
        return np.sum(partial_log_likelihood)


    def estimate_ps(self):
        subsets = [
            (self._first_community_members, self._first_community_members), 
            (self._first_community_members, self._second_community_members), 
            (self._second_community_members, self._second_community_members), 
        ]
        probas = []
        for subset_i, subset_j in subsets:
            matrix = self.get_only_community_members_subset(subset_i, subset_j)
            probas.append(self.N_g(matrix, 1)/(self.N_g(matrix, 0) + self.N_g(matrix, 1)))
        return probas

    @staticmethod
    def estimate_ps_no_matrix(N_gs, community_sizes):
        N_gs_1 = N_gs[0]
        N_gs_12 = N_gs[1]
        N_gs_2 = N_gs[2]
        proba_1 = N_gs_1/comb(community_sizes[0], 2)
        proba_12 = N_gs_12/(community_sizes[0]*community_sizes[1])
        proba_2 = N_gs_2/comb(community_sizes[1], 2)
        return [proba_1, proba_12, proba_2]
    
    def log_likelihood_no_matrix(self, N_gs, community_sizes):
        probas = self.estimate_ps_no_matrix(N_gs, community_sizes)
        N_gs_1_1 = N_gs[0]
        N_gs_12_1 = N_gs[1]
        N_gs_2_1 = N_gs[2]
        N_gs_1_0 = comb(community_sizes[0], 2) - N_gs[0]
        N_gs_12_0 = (community_sizes[0]*community_sizes[1]) - N_gs[1]
        N_gs_2_0 = comb(community_sizes[1], 2) - N_gs[2] 
        N_gs = [(N_gs_1_0, N_gs_1_1),(N_gs_12_0, N_gs_12_1),(N_gs_2_0, N_gs_2_1)]
        partial_log_likelihood = []
        for N_g, prob in zip(N_gs, probas):
            print(f"N_g: {N_g}")
            print(f"Prob: {prob}")
            partial_log_likelihood.append(N_g[1]*np.log(prob) + N_g[0]*np.log(1-prob))
            print(partial_log_likelihood)
        return np.sum(partial_log_likelihood)


def main():
    first_community_members = [1,2,3]
    second_community_members = [4,5,6]
    matrix = [
        [0,1,0,1,0,1], 
        [1,0,1,0,1,0], 
        [0,1,0,1,0,1], 
        [1,0,1,0,1,0],
        [0,1,0,1,0,0], 
        [1,0,1,0,0,0]
    ]
    rbm = RandomBlocksModel(
        first_community_members, 
        second_community_members, 
        matrix
    )
    return rbm


def coin_flip(proba):
        unif = np.random.uniform()
        return unif < proba

results = []
for _ in range(50000):
    connections = 0
    for _ in range(100):
        if coin_flip(0.8):
            connections += 1
    results.append(connections)
