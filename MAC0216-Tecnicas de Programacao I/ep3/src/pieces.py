"""!
@file pieces.py
@brief Implementação das peças do jogo Tetris
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

class Piece(ABC):
    """!
    @brief Classe base abstrata para todas as peças do Tetris
    
    @details Define a interface comum e comportamento básico para todas as peças do jogo.
    Cada peça possui uma posição no tabuleiro, um símbolo para representação visual
    e um estado de rotação que determina sua orientação atual.
    """
    
    def __init__(self, x: int, y: int, symbol: str):
        """!
        @brief Inicializa uma nova peça
        
        @param x Posição vertical inicial
        @param y Posição horizontal inicial
        @param symbol Caractere usado para representação visual
        """
        self._x = x
        self._y = y
        self._symbol = symbol
        self._rotation = 0
        self._shape = self._get_shape()
    
    @property
    def x(self) -> int:
        """!
        @brief Retorna a posição vertical atual da peça
        @return int Posição vertical
        """
        return self._x
    
    @x.setter
    def x(self, value: int):
        """!
        @brief Define a posição vertical da peça
        @param value Nova posição vertical
        """
        self._x = value
    
    @property
    def y(self) -> int:
        """!
        @brief Retorna a posição horizontal atual da peça
        @return int Posição horizontal
        """
        return self._y
    
    @y.setter
    def y(self, value: int):
        """!
        @brief Define a posição horizontal da peça
        @param value Nova posição horizontal
        """
        self._y = value
        
    @property
    def symbol(self) -> str:
        """!
        @brief Retorna o símbolo usado para representar a peça
        @return str Símbolo da peça
        """
        return self._symbol
    
    @property
    def shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Retorna a forma atual da peça
        @return List[Tuple[int, int]] Lista de coordenadas relativas
        """
        return self._shape
    
    @abstractmethod
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as coordenadas dos blocos que compõem a peça
        
        @details Método abstrato que deve ser implementado por cada tipo de peça.
        Define as coordenadas relativas dos blocos em cada rotação possível.
        
        @return List[Tuple[int, int]] Lista de coordenadas relativas
        """
        pass
    
    def rotate_left(self):
        """!
        @brief Rotaciona a peça 90 graus no sentido anti-horário
        """
        self._rotation = (self._rotation - 1) % 4
        self._shape = self._get_shape()
    
    def rotate_right(self):
        """!
        @brief Rotaciona a peça 90 graus no sentido horário
        """
        self._rotation = (self._rotation + 1) % 4
        self._shape = self._get_shape()

class IPiece(Piece):
    """!
    @brief Implementação da peça I do Tetris
    
    @details Representa uma peça em forma de linha reta composta por quatro blocos.
    Pode ser rotacionada em duas orientações principais: vertical e horizontal.
    
    Formato:
      []
      []
      []
      []
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as rotações possíveis da peça I
        @return List[Tuple[int, int]] Coordenadas dos blocos para a rotação atual
        """
        shapes = [
            [(0,1), (1,1), (2,1), (3,1)],  # vertical
            [(1,0), (1,1), (1,2), (1,3)],  # horizontal
            [(0,2), (1,2), (2,2), (3,2)],  # vertical
            [(2,0), (2,1), (2,2), (2,3)]   # horizontal
        ]
        return shapes[self._rotation]

class JPiece(Piece):
    """!
    @brief Implementação da peça J do Tetris
    
    @details Representa uma peça em forma de L invertido, composta por três blocos
    verticais e um bloco horizontal na base.
    
    Formato:
       []
       []
     [][]
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as rotações possíveis da peça J
        @return List[Tuple[int, int]] Coordenadas dos blocos para a rotação atual
        """
        shapes = [
            [(0,0), (1,0), (2,0), (2,1)],  # ┐ forma
            [(0,0), (0,1), (0,2), (1,0)],  # ┌ forma
            [(0,0), (0,1), (1,1), (2,1)],  # └ forma
            [(1,0), (1,1), (1,2), (0,2)]   # ┘ forma
        ]
        return shapes[self._rotation]

class LPiece(Piece):
    """!
    @brief Implementação da peça L do Tetris
    
    @details Representa uma peça em forma de L, composta por três blocos
    verticais e um bloco horizontal na base.
    
    Formato:
     []
     []
     [][]
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as rotações possíveis da peça L
        @return List[Tuple[int, int]] Coordenadas dos blocos para a rotação atual
        """
        shapes = [
            [(0,1), (1,1), (2,1), (2,0)],  # ┌ forma
            [(0,0), (0,1), (0,2), (1,2)],  # ┐ forma
            [(0,0), (0,1), (1,0), (2,0)],  # └ forma
            [(0,0), (1,0), (1,1), (1,2)]   # ┘ forma
        ]
        return shapes[self._rotation]

class OPiece(Piece):
    """!
    @brief Implementação da peça O do Tetris
    
    @details Representa uma peça quadrada 2x2 que não muda de forma ao rotacionar.
    É a única peça que mantém a mesma forma em todas as rotações.
    
    Formato:
     [][]
     [][]
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Retorna a forma da peça O (sempre a mesma)
        @return List[Tuple[int, int]] Coordenadas dos blocos que formam o quadrado
        """
        return [(0,0), (0,1), (1,0), (1,1)]

class SPiece(Piece):
    """!
    @brief Implementação da peça S do Tetris
    
    @details Representa uma peça em forma de S, que pode ser rotacionada em duas
    orientações principais: horizontal e vertical.
    
    Formato:
      [][]
    [][]
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as rotações possíveis da peça S
        @return List[Tuple[int, int]] Coordenadas dos blocos para a rotação atual
        """
        shapes = [
            [(1,0), (1,1), (0,1), (0,2)],  # horizontal ┌─┐
            [(0,1), (1,1), (1,2), (2,2)],  # vertical   └─┘
            [(2,0), (2,1), (1,1), (1,2)],  # horizontal
            [(0,0), (1,0), (1,1), (2,1)]   # vertical
        ]
        return shapes[self._rotation]

class TPiece(Piece):
    """!
    @brief Implementação da peça T do Tetris
    
    @details Representa uma peça em forma de T, composta por três blocos
    horizontais e um bloco vertical no centro.
    
    Formato:
     [][][]
       []
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as rotações possíveis da peça T
        @return List[Tuple[int, int]] Coordenadas dos blocos para a rotação atual
        """
        shapes = [
            [(0,1), (1,0), (1,1), (1,2)],  # ┴ forma
            [(0,0), (1,0), (2,0), (1,1)],  # ├ forma
            [(1,0), (1,1), (1,2), (2,1)],  # ┬ forma
            [(1,0), (0,1), (1,1), (2,1)]   # ┤ forma
        ]
        return shapes[self._rotation]

class ZPiece(Piece):
    """!
    @brief Implementação da peça Z do Tetris
    
    @details Representa uma peça em forma de Z, que pode ser rotacionada em duas
    orientações principais: horizontal e vertical.
    
    Formato:
    [][]
      [][]
    """
    def _get_shape(self) -> List[Tuple[int, int]]:
        """!
        @brief Define as rotações possíveis da peça Z
        @return List[Tuple[int, int]] Coordenadas dos blocos para a rotação atual
        """
        shapes = [
            [(0,0), (0,1), (1,1), (1,2)],  # horizontal
            [(0,2), (1,1), (1,2), (2,1)],  # vertical
            [(1,0), (1,1), (2,1), (2,2)],  # horizontal
            [(0,1), (1,0), (1,1), (2,0)]   # vertical
        ]
        return shapes[self._rotation]