"""!
@file controller.py
@brief Implementação do controlador principal do jogo
"""

import os
import pygame

from readchar import readkey, key
from src.game import Game, GameOverException
from src.scores import ScoreManager
from src.views import PyGameView, ConsoleView

class GameController:
    """!
    @brief Controlador principal do jogo Tetris
    
    @details Gerencia a interação entre o jogo, as visualizações e o sistema de pontuação.
    Processa entrada do usuário e coordena as atualizações do jogo.
    """
    
    def __init__(self, rows: int, cols: int):
        """!
        @brief Inicializa o controlador do jogo
        
        @param rows Número de linhas do tabuleiro
        @param cols Número de colunas do tabuleiro
        """
        self.rows = rows
        self.cols = cols
        self.game = Game()
        self.score_manager = ScoreManager()
    
    def play_game(self, name: str, use_pygame: bool = False, new_game: bool = False) -> None:
        """!
        @brief Loop principal do jogo para uma partida nova ou carregada
        
        @details Gerencia o ciclo de jogo, processando entradas e atualizando a visualização
        
        @param name Nome do jogador
        @param use_pygame Se True, usa interface PyGame; se False, usa console
        @param new_game Se True, inicia novo jogo; se False, continua jogo existente
        """
        try:
            if not self.game.board or new_game:
                self.game.initialize_game(self.rows, self.cols, name)
            
            view = PyGameView(self.rows, self.cols) if use_pygame else ConsoleView()
            clock = pygame.time.Clock() if use_pygame else None
            
            while True:
                view.display(self.game)
                
                if use_pygame:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            view.cleanup()
                            return
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP:
                                if self.game.current_piece:
                                    self.game.try_rotation('right')
                            elif event.key == pygame.K_s:
                                view.cleanup()
                                return
                            elif event.key == pygame.K_g:
                                self.game.save_game()
                                view.show_save_message("Jogo salvo!")
                    
                    view.handle_key_holds(self.game)
                    clock.tick(60)
                else:
                    k = readkey()
                    if k == key.LEFT:
                        self.game.move_piece('left')
                    elif k == key.RIGHT:
                        self.game.move_piece('right')
                    elif k == key.DOWN:
                        self.game.move_piece('down')
                    elif k == key.UP:
                        if self.game.current_piece:
                            self.game.try_rotation('right')
                    elif k == 's':
                        break
                    elif k == 'g':
                        self.game.save_game()
                        print("\nJogo salvo!")
                        input("Pressione Enter para continuar...")
                        break
                        
        except GameOverException:
            if use_pygame:
                view.cleanup()
            print("Fim de Jogo!")
            print(f"Pontuação Final: {self.game.score}")
            self.score_manager.save_score(self.game.player_name, self.game.score)
            input("Pressione Enter para continuar...")
    
    def load_saved_game(self) -> bool:
        """!
        @brief Gerencia o carregamento de um jogo salvo
        
        @details Exibe lista de jogos salvos e permite ao usuário selecionar um para carregar
        
        @return bool True se um jogo foi carregado com sucesso, False caso contrário
        """
        print("\nJogos salvos:")
        saved_games = [f for f in os.listdir() if f.endswith('.pkl')]
        
        if not saved_games:
            print("Nenhum jogo salvo encontrado!")
            input("Pressione Enter para continuar...")
            return False
            
        for i, filename in enumerate(saved_games, 1):
            print(f"{i}. {filename}")
            
        try:
            choice = int(input("\nSelecione um jogo para carregar (número): ")) - 1
            if 0 <= choice < len(saved_games):
                self.game = Game.load_game(saved_games[choice])
                print("Jogo carregado com sucesso!")
                return True
            else:
                print("Escolha inválida!")
        except (ValueError, IndexError):
            print("Entrada inválida!")
        
        input("Pressione Enter para continuar...")
        return False
    
    def show_high_scores(self) -> None:
        """!
        @brief Exibe as maiores pontuações registradas no sistema
        
        @details Mostra uma tabela com o ranking dos jogadores, incluindo nome e pontuação
        """
        scores = self.score_manager.get_high_scores()
        print("\n*** Top 10 Maiores Pontuações ***\n")
        if not scores:
            print("Nenhuma pontuação registrada!")
        else:
            print("Pos.  Jogador         Pontos")
            print("-" * 30)
            for i, score in enumerate(scores, 1):
                print(f"{i:4d}  {score['name']:<15} {score['score']:5d}")
        print("\nPressione Enter para continuar...")
        input()