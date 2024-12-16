import pytest
import pygame
import os
from unittest.mock import Mock, patch, MagicMock, call
from src.views import ConsoleView, PyGameView
from src.game import Game

class TestViews:
    @pytest.fixture
    def mock_game(self):
        """Cria uma instância simulada do jogo para testes"""
        game = Mock(spec=Game)
        game.board = Mock()
        game.board.rows = 20
        game.board.cols = 10
        game.board.grid = [[' ' for _ in range(10)] for _ in range(20)]
        game.score = 1000
        game.player_name = "Jogador Teste"
        game.current_piece = Mock()
        game.current_piece.shape = [(0, 0), (0, 1)]  # Forma simples para teste
        game.current_piece.symbol = '*'
        game.current_piece.x = 0
        game.current_piece.y = 0
        game._upcoming_pieces = [(Mock(), '*'), (Mock(), '@')]
        game._get_piece_preview = Mock(return_value=[
            [' ', '*', ' ', ' '],
            [' ', '*', ' ', ' '],
            [' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ']
        ])
        return game

    class TestConsoleView:
        @pytest.fixture
        def console_view(self):
            """Cria uma instância da visualização de console para testes"""
            return ConsoleView()

        @patch('os.system')
        def test_display_console(self, mock_system, console_view, mock_game):
            """Testa a exibição do jogo no console"""
            console_view.display(mock_game)
            # Verifica se a tela foi limpa
            mock_system.assert_called_once_with('cls||clear')

        def test_cleanup_console(self, console_view):
            """Testa a limpeza da visualização do console"""
            # Cleanup não deve fazer nada no modo console
            console_view.cleanup()

    class TestPyGameView:
        @pytest.fixture
        def mock_font(self):
            """Cria um mock do objeto Font do pygame"""
            font_mock = MagicMock()
            font_surface = MagicMock()
            font_surface.get_rect.return_value = MagicMock(centerx=0, centery=0)
            font_mock.render.return_value = font_surface
            return font_mock

        @pytest.fixture
        def pygame_view(self, mock_font):
            """Cria uma instância da visualização PyGame para testes"""
            with patch('pygame.init'), \
                 patch('pygame.display.set_mode', return_value=MagicMock()), \
                 patch('pygame.display.set_caption'), \
                 patch('pygame.font.Font', return_value=mock_font):
                view = PyGameView(20, 10)
                view.screen = MagicMock()
                view.font = mock_font
                view.small_font = mock_font
                return view

        def test_display_pygame(self, pygame_view, mock_game):
            """Testa a exibição do jogo usando PyGame"""
            with patch('pygame.display.flip') as mock_flip, \
                 patch.object(pygame_view, '_draw_grid') as mock_draw_grid, \
                 patch.object(pygame_view, '_draw_next_pieces') as mock_draw_next, \
                 patch.object(pygame_view, '_draw_score_and_controls') as mock_draw_score:
                
                pygame_view.display(mock_game)
                
                mock_draw_grid.assert_called_once_with(mock_game)
                mock_draw_next.assert_called_once_with(mock_game)
                mock_draw_score.assert_called_once_with(mock_game)
                mock_flip.assert_called_once()

        @patch('pygame.quit')
        def test_cleanup_pygame(self, mock_quit, pygame_view):
            """Testa a limpeza dos recursos do PyGame"""
            pygame_view.cleanup()
            mock_quit.assert_called_once()

        def test_show_save_message(self, pygame_view):
            """Testa a exibição da mensagem de salvamento"""
            with patch('pygame.time.get_ticks', return_value=0):
                message = "Jogo salvo!"
                pygame_view.show_save_message(message)
                assert pygame_view.save_message is not None
                assert pygame_view.save_message[0] == message

        def test_save_message_timeout(self, pygame_view):
            """Testa o timeout da mensagem de salvamento"""
            with patch('pygame.time.get_ticks') as mock_ticks:
                mock_ticks.return_value = 0
                pygame_view.show_save_message("Teste")
                
                mock_ticks.return_value = pygame_view.message_duration + 100
                
                with patch.object(pygame_view, '_draw_grid'), \
                     patch.object(pygame_view, '_draw_next_pieces'), \
                     patch.object(pygame_view, '_draw_score_and_controls'), \
                     patch('pygame.display.flip'):
                    pygame_view.display(Mock(spec=Game))
                
                assert pygame_view.save_message is None

        def test_handle_key_holds(self, pygame_view, mock_game):
            """Testa o processamento de teclas mantidas pressionadas"""
            mock_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False}
            
            with patch('pygame.key.get_pressed', return_value=mock_keys), \
                 patch('pygame.time.get_ticks', return_value=0):
                
                pygame_view.handle_key_holds(mock_game)
                mock_game.move_piece.assert_called_once_with('left')

        def test_draw_grid(self, pygame_view, mock_game):
            """Testa o desenho da grade do jogo"""
            with patch('pygame.draw.rect') as mock_rect:
                pygame_view._draw_grid(mock_game)
                assert mock_rect.call_count > 0

        def test_get_piece_offset(self, pygame_view):
            """Testa o cálculo do deslocamento para centralização das peças"""
            preview = [
                [' ', '*', ' ', ' '],
                [' ', '*', ' ', ' '],
                [' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ']
            ]
            
            offset_x, offset_y = pygame_view._get_piece_offset(preview)
            assert isinstance(offset_x, int)
            assert isinstance(offset_y, int)

        def test_draw_next_pieces(self, pygame_view, mock_game):
            """Testa o desenho das próximas peças"""
            with patch('pygame.draw.rect') as mock_rect, \
                 patch.object(pygame_view.font, 'render') as mock_render:
                
                surface_mock = MagicMock()
                mock_render.return_value = surface_mock
                
                # Configura o mock para _get_piece_preview
                mock_game._get_piece_preview.return_value = [
                    [' ', '*', ' ', ' '],
                    [' ', '*', ' ', ' '],
                    [' ', ' ', ' ', ' '],
                    [' ', ' ', ' ', ' ']
                ]
                
                pygame_view._draw_next_pieces(mock_game)
                assert mock_rect.call_count > 0
                mock_render.assert_called_with("Próximas:", True, (255, 255, 255))

        def test_draw_score_and_controls(self, pygame_view, mock_game):
            """Testa o desenho da pontuação e controles"""
            with patch.object(pygame_view.font, 'render') as mock_render:
                surface_mock = MagicMock()
                mock_render.return_value = surface_mock
                
                pygame_view._draw_score_and_controls(mock_game)
                
                # Verifica se foram feitas as chamadas de renderização esperadas
                expected_calls = [
                    call("Pontuação:", True, (255, 255, 255)),
                    call(str(mock_game.score), True, (255, 255, 255))
                ]
                mock_render.assert_has_calls(expected_calls, any_order=True)
                assert mock_render.call_count >= 2

        def test_initialization(self):
            """Testa a inicialização da visualização PyGame"""
            with patch('pygame.init'), \
                 patch('pygame.display.set_mode', return_value=MagicMock()) as mock_set_mode, \
                 patch('pygame.display.set_caption') as mock_set_caption, \
                 patch('pygame.font.Font', return_value=MagicMock()):
                
                view = PyGameView(20, 10)
                
                mock_set_mode.assert_called_once()
                mock_set_caption.assert_called_once_with("Tetris PyGame")
                
                assert view.width == 10 * view.CELL_SIZE + view.sidebar_width
                assert view.height == 20 * view.CELL_SIZE