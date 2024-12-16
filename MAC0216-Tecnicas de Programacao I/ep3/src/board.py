"""!
@file board.py
@brief Implementação do tabuleiro do jogo e sua lógica
"""

from typing import List
from src.pieces import Piece

class Board:
    """!
    @brief Representa o tabuleiro do jogo onde as peças são colocadas e a lógica acontece
    
    O tabuleiro é uma grade bidimensional onde as peças são posicionadas
    e onde ocorre toda a lógica do jogo.
    """
    
    def __init__(self, rows: int, cols: int):
        """!
        @brief Inicializa um novo tabuleiro de jogo
        @param rows Número de linhas no tabuleiro
        @param cols Número de colunas no tabuleiro
        """
        self._rows = rows
        self._cols = cols
        self._grid = [[' ' for _ in range(cols)] for _ in range(rows)]
    
    @property
    def rows(self) -> int:
        """!
        @brief Retorna o número de linhas no tabuleiro
        @return int Número de linhas
        """
        return self._rows
    
    @property
    def cols(self) -> int:
        """!
        @brief Retorna o número de colunas no tabuleiro
        @return int Número de colunas
        """
        return self._cols
    
    @property
    def grid(self) -> List[List[str]]:
        """!
        @brief Retorna a grade atual do tabuleiro
        @return List[List[str]] Grade do tabuleiro
        """
        return self._grid
        
    def is_valid_move(self, piece: Piece, x: int, y: int) -> bool:
        """!
        @brief Verifica se um movimento é válido para uma peça específica
        @param piece A peça a ser verificada
        @param x Posição X desejada
        @param y Posição Y desejada
        @return bool True se o movimento é válido, False caso contrário
        """
        # Validate initial position
        if x < 0 or y < 0:
            return False
            
        for dx, dy in piece.shape:
            new_x, new_y = x + dx, y + dy
            if (new_x < 0 or new_x >= self._rows or 
                new_y < 0 or new_y >= self._cols or 
                self._grid[new_x][new_y] != ' '):
                return False
        return True
    
    def place_piece(self, piece: Piece):
        """!
        @brief Posiciona uma peça no tabuleiro permanentemente
        @param piece A peça a ser posicionada
        @raises ValueError Se a peça estiver em posição inválida
        """
        # First verify if the move is valid
        if not self.is_valid_move(piece, piece.x, piece.y):
            raise ValueError("Tentativa de colocar peça em posição inválida")
            
        for dx, dy in piece.shape:
            new_x, new_y = piece.x + dx, piece.y + dy
            # Extra safety check - should never trigger if is_valid_move is correct
            if (new_x < 0 or new_x >= self._rows or 
                new_y < 0 or new_y >= self._cols):
                raise ValueError("Posição fora dos limites do tabuleiro")
                
            self._grid[new_x][new_y] = piece.symbol
            
    def clear_lines(self) -> int:
        """!
        @brief Limpa as linhas completas do tabuleiro e move as linhas acima para baixo
        @return int Número de linhas removidas
        """
        lines_cleared = 0
        y = self._rows - 1
        while y >= 0:
            if all(self._grid[y][x] != ' ' for x in range(self._cols)):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self._grid[y2] = self._grid[y2-1].copy()
                self._grid[0] = [' ' for _ in range(self._cols)]
            else:
                y -= 1
        return lines_cleared