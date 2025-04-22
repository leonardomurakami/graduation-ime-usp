"""!
@file game.py
@brief Implementação da lógica principal do jogo
"""

import os
import pickle
from datetime import datetime
from typing import Optional, Type
from random import choice
from src.pieces import (Piece, IPiece, JPiece, LPiece, OPiece, 
                   SPiece, TPiece, ZPiece)
from src.board import Board

class GameOverException(Exception):
    """!
    @brief Exceção lançada quando o jogo termina (não é mais possível posicionar peças)
    """
    pass

class Game:
    """!
    @brief Classe principal que gerencia a lógica do jogo Tetris
    
    @details Controla o fluxo do jogo, incluindo a geração de peças,
    movimentação, pontuação e estado do jogo.
    """
    
    ##! Dicionário que mapeia identificadores de peças para suas respectivas classes e símbolos
    PIECE_TYPES = {
        'I': (IPiece, '*'),
        'J': (JPiece, '@'),
        'L': (LPiece, '#'),
        'O': (OPiece, '$'),
        'S': (SPiece, '%'),
        'T': (TPiece, '&'),
        'Z': (ZPiece, '?')
    }
    
    def __init__(self):
        """!
        @brief Inicializa uma nova instância do jogo
        """
        self._board: Optional[Board] = None
        self._current_piece: Optional[Piece] = None
        self._upcoming_pieces = []
        self._score = 0
        self._player_name = ""
        self._preview_size = 3
    
    @property
    def score(self) -> int:
        """!
        @brief Retorna a pontuação atual do jogador
        @return int Pontuação atual
        """
        return self._score
    
    @property
    def player_name(self) -> str:
        """!
        @brief Retorna o nome do jogador atual
        @return str Nome do jogador
        """
        return self._player_name
    
    @property
    def current_piece(self) -> Optional[Piece]:
        """!
        @brief Retorna a peça atual em movimento
        @return Optional[Piece] Peça atual ou None se não houver
        """
        return self._current_piece
    
    @property
    def board(self) -> Optional[Board]:
        """!
        @brief Retorna o tabuleiro atual do jogo
        @return Optional[Board] Tabuleiro atual ou None se não inicializado
        """
        return self._board
        
    def initialize_game(self, rows: int, cols: int, player_name: str):
        """!
        @brief Inicializa um novo jogo com as dimensões e jogador especificados
        
        @param rows Número de linhas do tabuleiro
        @param cols Número de colunas do tabuleiro
        @param player_name Nome do jogador
        """
        self._board = Board(rows, cols)
        self._score = 0
        self._player_name = player_name
        self._upcoming_pieces = []
        self._fill_upcoming_pieces()
        self._spawn_piece()
        
    def _fill_upcoming_pieces(self):
        """!
        @brief Preenche a fila de próximas peças
        
        @details Mantém a fila de próximas peças com o tamanho definido em preview_size,
        selecionando peças aleatoriamente do conjunto disponível
        """
        while len(self._upcoming_pieces) < self._preview_size:
            piece_type, symbol = choice(list(self.PIECE_TYPES.values()))
            self._upcoming_pieces.append((piece_type, symbol))
    
    def _spawn_piece(self):
        """!
        @brief Gera uma nova peça atual no topo do tabuleiro
        
        @throws ValueError Se o tabuleiro não estiver inicializado
        @throws GameOverException Se não for possível posicionar a nova peça
        """
        if not self._board:
            raise ValueError("Tabuleiro não inicializado")
        
        piece_type, symbol = self._upcoming_pieces.pop(0)
        self._current_piece = piece_type(0, self._board.cols//2, symbol)
        
        self._fill_upcoming_pieces()
        
        if not self._board.is_valid_move(self._current_piece, 
                                       self._current_piece.x, 
                                       self._current_piece.y):
            raise GameOverException()
    
    def try_rotation(self, direction: str) -> bool:
        """!
        @brief Tenta rotacionar a peça atual na direção especificada
        
        @details Implementa o sistema de "wall kicks" - se a rotação inicial não for
        possível, tenta pequenos ajustes na posição para permitir a rotação.
        Referência para wallkick: https://tetris.fandom.com/wiki/Wall_kick
        
        @param direction Direção da rotação ('right' ou 'left')
        @return bool True se a rotação foi bem-sucedida, False caso contrário
        """
        if not self._current_piece or not self._board:
            return False
            
        original_x = self._current_piece.x
        original_y = self._current_piece.y
        original_shape = self._current_piece.shape.copy()
        
        if direction == 'right':
            self._current_piece.rotate_right()
        else:
            self._current_piece.rotate_left()
        
        if self._board.is_valid_move(self._current_piece, 
                                    self._current_piece.x, 
                                    self._current_piece.y):
            return True
        
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if self._board.is_valid_move(self._current_piece,
                                       self._current_piece.x + dx,
                                       self._current_piece.y + dy):
                self._current_piece.x += dx
                self._current_piece.y += dy
                return True
        
        self._current_piece.x = original_x
        self._current_piece.y = original_y
        self._current_piece._shape = original_shape
        return False
    
    def move_piece(self, direction: str) -> bool:
        """!
        @brief Move a peça atual na direção especificada
        
        @details Se a peça não puder se mover para baixo, ela é fixada no tabuleiro
        e uma nova peça é gerada.
        
        @param direction Direção do movimento ('left', 'right' ou 'down')
        @return bool True se o movimento foi realizado, False caso contrário
        """
        if not self._current_piece or not self._board:
            return False
            
        dx, dy = {
            'left': (0, -1),
            'right': (0, 1),
            'down': (1, 0)
        }[direction]
        
        new_x = self._current_piece.x + dx
        new_y = self._current_piece.y + dy
        
        if self._board.is_valid_move(self._current_piece, new_x, new_y):
            self._current_piece.x = new_x
            self._current_piece.y = new_y
            return True
        elif direction == 'down':
            self._board.place_piece(self._current_piece)
            lines_cleared = self._board.clear_lines()
            self._score += self._calculate_score(lines_cleared)
            self._spawn_piece()
            return False
        return False
    
    def _get_piece_preview(self, piece_type: Type[Piece], symbol: str) -> list[str]:
        """!
        @brief Gera uma grade de prévia 4x4 para uma peça
        
        @param piece_type Tipo da peça a ser visualizada
        @param symbol Símbolo usado para representar a peça
        @return list[str] Grade 4x4 contendo a prévia da peça
        """
        preview = [[' ' for _ in range(4)] for _ in range(4)]
        offset_x = 0 if piece_type == IPiece else 1
        offset_y = 0 if piece_type == IPiece else 1
        
        piece = piece_type(offset_x, offset_y, symbol)
        
        for dx, dy in piece.shape:
            new_x = dx + offset_x
            new_y = dy + offset_y
            if 0 <= new_x < 4 and 0 <= new_y < 4:
                preview[new_x][new_y] = symbol
            
        return preview
    
    def _calculate_score(self, lines: int) -> int:
        """!
        @brief Calcula a pontuação baseada no número de linhas removidas
        
        @param lines Número de linhas removidas simultaneamente
        @return int Pontos ganhos pela remoção das linhas
        """
        points = {1: 100, 2: 300, 3: 500, 4: 800}
        return points.get(lines, 0)
    
    def save_game(self):
        """!
        @brief Salva o estado atual do jogo em um arquivo
        
        @details O nome do arquivo é gerado usando o nome do jogador e timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._player_name}_{timestamp}.pkl"
        with open(filename, "wb") as f:
            pickle.dump(self, f)
            
    @staticmethod
    def load_game(filename: str) -> 'Game':
        """!
        @brief Carrega um jogo salvo a partir de um arquivo
        
        @param filename Nome do arquivo a ser carregado
        @return Game Instância do jogo carregado
        """
        with open(filename, "rb") as f:
            return pickle.load(f)