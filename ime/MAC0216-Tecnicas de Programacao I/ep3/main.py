"""!
@file main.py
@brief Ponto de entrada principal do jogo Tetris
"""
import os

from readchar import readkey
from src.controller import GameController

NUM_ROWS = 20
NUM_COLS = 10

def main():
    """!
    @brief Função principal que inicializa e executa o jogo Tetris
    
    @details Gerencia o menu principal e suas opções, permitindo ao jogador:
    - Iniciar novo jogo em modo texto
    - Iniciar novo jogo em modo visual (PyGame)
    - Carregar um jogo salvo
    - Ver pontuações mais altas
    - Sair do jogo
    """
    controller = GameController(NUM_ROWS, NUM_COLS)
    
    while True:
        print()
        print("""
            
  _______ ________   _________ _____  _____  _____ 
 |__   __|  ____\ \ / /__   __|  __ \|_   _|/ ____|
    | |  | |__   \ V /   | |  | |__) | | | | (___  
    | |  |  __|   > <    | |  |  _  /  | |  \___ \ 
    | |  | |____ / . \   | |  | | \ \ _| |_ ____) |
    |_|  |______/_/ \_\  |_|  |_|  \_\_____|_____/ 
                                                   
        """)
        print()
        print("Opções do jogo:")
        print("- <i> para iniciar uma nova partida em modo texto")
        print("- <v> para iniciar uma nova partida com UI (PyGame)")
        print("- <c> para carregar uma partida gravada e continuá-la")
        print("- <p> para ver as 10 melhores pontuações")
        print("- <s> para sair do jogo")
        
        option = readkey()
        
        if option == 'i':
            name = input("Digite o nome do jogador: ")
            controller.play_game(name, use_pygame=False, new_game=True)
        elif option == 'v':
            name = input("Digite o nome do jogador: ")
            controller.play_game(name, use_pygame=True, new_game=True)
        elif option == 'c':
            if controller.load_saved_game():
                print("Selecione o modo de visualização:")
                print("1. Modo texto")
                print("2. Modo GUI")
                view_choice = input("Escolha (1/2): ")
                controller.play_game("", use_pygame=(view_choice == "2"))
        elif option == 'p':
            controller.show_high_scores()
        elif option == 's':
            break

if __name__ == "__main__":
    main()