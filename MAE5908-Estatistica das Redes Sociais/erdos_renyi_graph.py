import numpy as np

class ErdosRenyiGraph:
    def __init__(
        self, 
        conn_matrix=None, 
        num_vertices=None, 
        probability_of_connection=None
    ):
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
        self._probability = (
            probability_of_connection 
            if conn_matrix is None 
            else self.estimate_p()
        )
    

    def __coin_flip(self):
        unif = np.random.uniform()
        return unif < self._probability

    def _populate_conn_matrix(self):
        matrix = np.empty(
            shape=(self._num_vertices, self._num_vertices),
            dtype=int
        )
        for i in range(self._num_vertices):
            for j in range(i, self._num_vertices):
                if i == j:
                    matrix[i, j] = 0
                else:
                    matrix[i, j] = self.__coin_flip()
        for j in range(self._num_vertices):
            for i in range(j, self._num_vertices):
                matrix[i, j] = matrix[j, i]
        return matrix


    def N_g(self, value):
        if value == 1:
            return self.connection_matrix.sum()/2
        elif value == 0:
            return (-(self.connection_matrix-1).sum())/2 - self._num_vertices
    
    def likelihood(self):
        #probabilidade conjunta do grafo G(N, p) ser exatamente M
        #chamada de verossimilhanca
        return np.power(
            self._probability, self.N_g(1)
        )*np.power(
            (1 - self._probability), self.N_g(0)
        )
    
    def estimate_p(self):
        #aula 18
        p_estimate = self.N_g(1)/(
                self._num_vertices*(self._num_vertices-1)/2
        )
        return p_estimate

def main():
    matrix = [
        [0,1,0,1,0,0], 
        [1,0,0,1,1,1], 
        [0,0,0,1,1,0], 
        [1,1,1,0,1,0],
        [0,1,1,1,0,1], 
        [0,1,0,0,1,0]
    ]
    edg = ErdosRenyiGraph(
        matrix
    )
    return edg

