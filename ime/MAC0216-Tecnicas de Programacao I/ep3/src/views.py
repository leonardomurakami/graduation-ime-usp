"""!
@file views.py
@brief Implementação das interfaces visuais do jogo
"""

import os
import pygame
from abc import ABC, abstractmethod
from typing import Optional, Dict, Tuple
from src.game import Game

class GameView(ABC):
    """!
    @brief Classe base abstrata para visualizações do jogo
    
    @details Define a interface comum para diferentes tipos de visualização.
    """
    
    @abstractmethod
    def display(self, game: Game) -> None:
        """!
        @brief Método abstrato para exibir o estado atual do jogo
        
        @param game Instância do jogo a ser exibida
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """!
        @brief Método abstrato para limpeza de recursos da visualização
        """
        pass

class ConsoleView(GameView):
    """!
    @brief Implementação da visualização do jogo em modo texto
    
    @details Exibe o jogo usando caracteres ASCII e comandos do terminal
    """
    
    def display(self, game: Game) -> None:
        """!
        @brief Exibe o estado atual do jogo no console
        
        @param game Instância do jogo a ser exibida
        """
        if not game.board:
            return
            
        os.system('cls||clear')
        
        print("\nControles:")
        print("←/→: Mover esquerda/direita  ↓: Mover para baixo")
        print("↑: Rotacionar    S: Sair    G: Salvar jogo\n")
        
        display_grid = [row.copy() for row in game.board.grid]
        if game.current_piece:
            for dx, dy in game.current_piece.shape:
                x, y = game.current_piece.x + dx, game.current_piece.y + dy
                if 0 <= x < game.board.rows and 0 <= y < game.board.cols:
                    display_grid[x][y] = game.current_piece.symbol
        
        print("+" + "-" * game.board.cols)
        for row_idx in range(game.board.rows):
            print("|" + "".join(display_grid[row_idx]) + "|")
        print("+" + "-" * game.board.cols + "+")
        print(f"Pontuação: {game.score}  Jogador: {game.player_name}")
    
    def cleanup(self) -> None:
        """!
        @brief Método de limpeza (vazio para visualização em console)
        """
        pass

class PyGameView:
    """!
    @brief Implementação da visualização do jogo usando PyGame
    
    @details Fornece uma interface gráfica com cores, animações e controles suaves
    """
    
    ##! Tamanho em pixels de cada célula do tabuleiro
    CELL_SIZE = 30
    
    ##! Mapeamento de símbolos para cores RGB
    COLORS = {
        '*': (0, 255, 255),    # Ciano para peça I
        '@': (0, 0, 255),      # Azul para peça J
        '#': (255, 127, 0),    # Laranja para peça L
        '$': (255, 255, 0),    # Amarelo para peça O
        '%': (0, 255, 0),      # Verde para peça S
        '&': (128, 0, 128),    # Roxo para peça T
        '?': (255, 0, 0),      # Vermelho para peça Z
        ' ': (40, 40, 40)      # Cinza escuro para células vazias
    }
    
    def __init__(self, rows: int, cols: int):
        """!
        @brief Inicializa a visualização PyGame
        
        @param rows Número de linhas do tabuleiro
        @param cols Número de colunas do tabuleiro
        """
        pygame.init()
        self.rows = rows
        self.cols = cols
        
        self.preview_width = 150
        self.info_width = 200
        self.sidebar_width = self.preview_width + self.info_width
        self.width = cols * self.CELL_SIZE + self.sidebar_width
        self.height = rows * self.CELL_SIZE
        
        self.preview_box_size = 90
        self.preview_cell_size = 20
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris PyGame")
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.held_keys: Dict[int, float] = {}
        self.key_repeat_delay = 200
        self.key_repeat_interval = 50
        
        self.save_message: Optional[Tuple[str, float]] = None
        self.message_duration = 2000
    
    def _draw_grid(self, game: Game) -> None:
        """!
        @brief Desenha a grade do jogo com as peças atuais
        
        @param game Instância do jogo a ser desenhada
        """
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (0, 0, self.cols * self.CELL_SIZE + 2, self.height),
            2
        )
        
        for y in range(game.board.rows):
            for x in range(game.board.cols):
                color = self.COLORS[game.board.grid[y][x]]
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x * self.CELL_SIZE + 1,
                     y * self.CELL_SIZE + 1,
                     self.CELL_SIZE - 1,
                     self.CELL_SIZE - 1)
                )
        
        if game.current_piece:
            for dx, dy in game.current_piece.shape:
                x = game.current_piece.y + dy
                y = game.current_piece.x + dx
                if 0 <= y < game.board.rows and 0 <= x < game.board.cols:
                    pygame.draw.rect(
                        self.screen,
                        self.COLORS[game.current_piece.symbol],
                        (x * self.CELL_SIZE + 1,
                         y * self.CELL_SIZE + 1,
                         self.CELL_SIZE - 1,
                         self.CELL_SIZE - 1)
                    )
    
    def _get_piece_offset(self, preview: list[list[str]]) -> tuple[int, int]:
        """!
        @brief Calcula o deslocamento necessário para centralizar uma peça na prévia
        
        @param preview Grade de prévia da peça
        @return tuple[int, int] Deslocamento (x, y) para centralização
        """
        min_row = 4
        max_row = -1
        min_col = 4
        max_col = -1
        
        for row in range(4):
            for col in range(4):
                if preview[row][col] != ' ':
                    min_row = min(min_row, row)
                    max_row = max(max_row, row)
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)
        
        if max_row == -1:
            return 0, 0
            
        piece_height = max_row - min_row + 1
        piece_width = max_col - min_col + 1
        
        offset_y = (4 - piece_height) // 2
        offset_x = (4 - piece_width) // 2
        
        return offset_x - min_col, offset_y - min_row
    
    def _draw_next_pieces(self, game: Game) -> None:
        """!
        @brief Desenha as próximas peças na área de prévia
        
        @param game Instância do jogo
        """
        preview_start_x = self.cols * self.CELL_SIZE + 20
        
        text = self.font.render("Próximas:", True, (255, 255, 255))
        self.screen.blit(text, (preview_start_x, 10))
        
        available_height = self.height - 50
        box_spacing = (available_height - len(game._upcoming_pieces) * self.preview_box_size) // (len(game._upcoming_pieces) + 1)
        
        for i, (piece_type, symbol) in enumerate(game._upcoming_pieces):
            preview = game._get_piece_preview(piece_type, symbol)
            preview_y = 50 + i * (self.preview_box_size + box_spacing)
            
            pygame.draw.rect(
                self.screen,
                (100, 100, 100),
                (preview_start_x, preview_y, self.preview_box_size, self.preview_box_size),
                1
            )
            
            offset_x, offset_y = self._get_piece_offset(preview)
            
            for row in range(4):
                for col in range(4):
                    if preview[row][col] != ' ':
                        px = preview_start_x + (offset_x + col) * self.preview_cell_size + (self.preview_box_size - 4 * self.preview_cell_size) // 2
                        py = preview_y + (offset_y + row) * self.preview_cell_size + (self.preview_box_size - 4 * self.preview_cell_size) // 2
                        pygame.draw.rect(
                            self.screen,
                            self.COLORS[symbol],
                            (px, py, self.preview_cell_size - 1, self.preview_cell_size - 1)
                        )
    
    def _draw_score_and_controls(self, game: Game) -> None:
        """!
        @brief Desenha a pontuação e controles na área de informações
        
        @param game Instância do jogo
        """
        info_start_x = self.cols * self.CELL_SIZE + self.preview_width + 20
        
        score_text = self.font.render("Pontuação:", True, (255, 255, 255))
        score_value = self.font.render(str(game.score), True, (255, 255, 255))
        name_text = self.small_font.render(f"Jogador: {game.player_name}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (info_start_x, 20))
        self.screen.blit(score_value, (info_start_x, 60))
        self.screen.blit(name_text, (info_start_x, 100))
        
        controls = [
            "Controles:",
            "Left/Right: Mover",
            "Down: Descer",
            "Up: Rotacionar",
            "S: Sair",
            "G: Salvar jogo"
        ]
        
        control_start_y = 160
        for i, text in enumerate(controls):
            surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (info_start_x, control_start_y + i * 30))
    
    def _draw_save_message(self) -> None:
        """!
        @brief Desenha a mensagem de salvamento do jogo, se houver
        """
        if self.save_message:
            message, timestamp = self.save_message
            current_time = pygame.time.get_ticks()
            
            if current_time - timestamp < self.message_duration:
                text = self.font.render(message, True, (0, 255, 0))
                text_rect = text.get_rect(center=(self.width // 2, 50))
                self.screen.blit(text, text_rect)
            else:
                self.save_message = None
    
    def show_save_message(self, message: str) -> None:
        """!
        @brief Define uma mensagem de salvamento para ser exibida
        
        @param message Mensagem a ser exibida
        """
        self.save_message = (message, pygame.time.get_ticks())
    
    def display(self, game: Game) -> None:
        """!
        @brief Atualiza a tela com o estado atual do jogo
        
        @param game Instância do jogo a ser exibida
        """
        self.screen.fill((0, 0, 0))
        self._draw_grid(game)
        self._draw_next_pieces(game)
        self._draw_score_and_controls(game)
        self._draw_save_message()
        pygame.display.flip()
    
    def cleanup(self) -> None:
        """!
        @brief Limpa os recursos do PyGame ao encerrar
        """
        pygame.quit()
    
    def handle_key_holds(self, game: Game) -> None:
        """!
        @brief Processa as teclas mantidas pressionadas para movimento contínuo
        
        @param game Instância do jogo
        """
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        for key, direction in [
            (pygame.K_LEFT, 'left'),
            (pygame.K_RIGHT, 'right'),
            (pygame.K_DOWN, 'down')
        ]:
            if keys[key]:
                if key not in self.held_keys:
                    self.held_keys[key] = current_time
                    game.move_piece(direction)
                else:
                    hold_time = current_time - self.held_keys[key]
                    if hold_time > self.key_repeat_delay:
                        moves = (hold_time - self.key_repeat_delay) // self.key_repeat_interval
                        if moves > 0:
                            game.move_piece(direction)
                            self.held_keys[key] = current_time - (
                                (hold_time - self.key_repeat_delay) % self.key_repeat_interval
                            )
            else:
                if key in self.held_keys:
                    del self.held_keys[key]