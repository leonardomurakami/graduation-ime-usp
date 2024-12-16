import pytest
import pygame
from unittest.mock import Mock, patch
from src.controller import GameController
from src.game import Game, GameOverException
from src.scores import ScoreManager

class TestGameController:
    @pytest.fixture
    def controller(self):
        """Cria uma instância do controlador para testes"""
        return GameController(20, 10)

    @pytest.fixture
    def mock_game(self):
        """Cria um mock do jogo para testes"""
        game = Mock(spec=Game)
        game.score = 0
        game.player_name = "Teste"
        game.board = Mock()
        return game

    def test_controller_initialization(self, controller):
        """Testa se o controlador é inicializado com valores corretos"""
        assert controller.rows == 20
        assert controller.cols == 10
        assert isinstance(controller.game, Game)
        assert isinstance(controller.score_manager, ScoreManager)

    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('src.controller.PyGameView')
    def test_play_game_new_game(self, mock_pygame_view, mock_clock, mock_caption, 
                               mock_display, mock_init, controller):
        """Testa inicialização de um novo jogo"""
        controller.game = Mock(spec=Game)
        mock_event = Mock()
        mock_event.type = pygame.QUIT
        
        # Simula fim do jogo após algumas iterações
        controller.game.initialize_game.return_value = None
        controller.game.score = 1000
        controller.game.player_name = "Jogador"
        
        # Simula pygame.event.get retornando o evento QUIT
        with patch('pygame.event.get', return_value=[mock_event]):
            controller.play_game("Jogador", use_pygame=True, new_game=True)
        
        controller.game.initialize_game.assert_called_once_with(20, 10, "Jogador")
        assert mock_pygame_view.return_value.cleanup.called
        
    @patch('src.controller.ConsoleView')
    def test_play_game_console_mode(self, mock_console_view, controller):
        """Testa o jogo em modo console"""
        controller.game = Mock(spec=Game)
        
        # Simula tecla 's' para sair após algumas iterações
        mock_console_view.return_value.display.return_value = None
        with patch('src.controller.readkey', return_value='s'):
            controller.play_game("Jogador", use_pygame=False)
            
        mock_console_view.return_value.display.assert_called()

    def test_play_game_game_over(self, controller):
        """Testa comportamento quando o jogo termina"""
        controller.game = Mock(spec=Game)
        controller.score_manager = Mock(spec=ScoreManager)
        
        # Simula GameOverException
        controller.game.score = 500
        controller.game.player_name = "Jogador"
        controller.game.initialize_game.side_effect = GameOverException
        
        with patch('builtins.input', return_value=''):
            controller.play_game("Jogador", use_pygame=False, new_game=True)
        
        controller.score_manager.save_score.assert_called_once_with("Jogador", 500)

    def test_load_saved_game_no_saves(self, controller):
        """Testa tentativa de carregar jogo quando não há jogos salvos"""
        with patch('os.listdir', return_value=[]):
            with patch('builtins.input', return_value=''):
                result = controller.load_saved_game()
                assert result == False

    @patch('os.listdir')
    @patch('src.game.Game.load_game')
    def test_load_saved_game_success(self, mock_load_game, mock_listdir, controller):
        """Testa carregamento bem-sucedido de um jogo salvo"""
        mock_listdir.return_value = ['save1.pkl', 'save2.pkl']
        mock_load_game.return_value = Mock(spec=Game)
        
        with patch('builtins.input', return_value='1'):
            result = controller.load_saved_game()
            assert result == True
            mock_load_game.assert_called_once_with('save1.pkl')

    @patch('os.listdir')
    def test_load_saved_game_invalid_choice(self, mock_listdir, controller):
        """Testa seleção inválida ao carregar jogo"""
        mock_listdir.return_value = ['save1.pkl', 'save2.pkl']
        
        # Testa com escolha inválida
        with patch('builtins.input', return_value='999'):
            result = controller.load_saved_game()
            assert result == False
        
        # Testa com entrada não numérica
        with patch('builtins.input', return_value='abc'):
            result = controller.load_saved_game()
            assert result == False

    def test_show_high_scores(self, controller):
        """Testa exibição de pontuações altas"""
        mock_scores = [
            {'name': 'Jogador1', 'score': 1000},
            {'name': 'Jogador2', 'score': 800}
        ]
        controller.score_manager = Mock(spec=ScoreManager)
        controller.score_manager.get_high_scores.return_value = mock_scores
        
        with patch('builtins.input', return_value=''):
            controller.show_high_scores()
            controller.score_manager.get_high_scores.assert_called_once()

    @patch('src.controller.PyGameView')
    def test_game_save_pygame(self, mock_pygame_view, controller):
        """Testa salvamento do jogo no modo PyGame"""
        controller.game = Mock(spec=Game)
        
        # Simula tecla 'g' para salvar e depois pygame.QUIT
        mock_event1 = Mock(type=pygame.KEYDOWN, key=pygame.K_g)
        mock_event2 = Mock(type=pygame.QUIT)
        mock_pygame_view.return_value.display.return_value = None
        
        with patch('pygame.event.get', side_effect=[[mock_event1], [mock_event2]]):
            controller.play_game("Jogador", use_pygame=True)
            
        controller.game.save_game.assert_called_once()
        mock_pygame_view.return_value.show_save_message.assert_called_once_with("Jogo salvo!")

    @patch('src.controller.ConsoleView')
    def test_game_save_console(self, mock_console_view, controller):
        """Testa salvamento do jogo no modo console"""
        controller.game = Mock(spec=Game)
        mock_console_view.return_value.display.return_value = None
        
        # Simula tecla 'g' para salvar
        with patch('src.controller.readkey', return_value='g'):
            with patch('builtins.input', return_value=''):
                controller.play_game("Jogador", use_pygame=False)
                
        controller.game.save_game.assert_called_once()