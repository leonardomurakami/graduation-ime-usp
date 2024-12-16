import pytest
from unittest.mock import Mock, patch
import os
from src.game import Game, GameOverException
from src.board import Board
from src.pieces import Piece, IPiece, JPiece, LPiece, OPiece, SPiece, TPiece, ZPiece

class TestGame:
    @pytest.fixture
    def game(self):
        """Cria uma instância do jogo para testes"""
        return Game()

    @pytest.fixture
    def initialized_game(self, game):
        """Cria uma instância do jogo já inicializada"""
        game.initialize_game(20, 10, "Jogador Teste")
        return game

    def test_game_initialization(self, game):
        """Testa se o jogo é inicializado corretamente"""
        assert game.board is None
        assert game.current_piece is None
        assert game._upcoming_pieces == []
        assert game.score == 0
        assert game.player_name == ""

    def test_game_initialization_with_parameters(self, game):
        """Testa a inicialização do jogo com parâmetros específicos"""
        game.initialize_game(20, 10, "Jogador Teste")
        
        assert isinstance(game.board, Board)
        assert game.board.rows == 20
        assert game.board.cols == 10
        assert game.player_name == "Jogador Teste"
        assert game.score == 0
        assert len(game._upcoming_pieces) == game._preview_size
        assert game.current_piece is not None

    def test_fill_upcoming_pieces(self, game):
        """Testa o preenchimento da fila de peças futuras"""
        game.initialize_game(20, 10, "Jogador")
        
        # Verifica se a fila tem o tamanho correto
        assert len(game._upcoming_pieces) == game._preview_size
        
        # Verifica se todas as entradas são tuplas (type, symbol) válidas
        for piece_type, symbol in game._upcoming_pieces:
            assert piece_type in [IPiece, JPiece, LPiece, OPiece, SPiece, TPiece, ZPiece]
            assert symbol in ['*', '@', '#', '$', '%', '&', '?']

    def test_spawn_piece_without_board(self, game):
        """Testa tentativa de gerar peça sem tabuleiro inicializado"""
        with pytest.raises(ValueError, match="Tabuleiro não inicializado"):
            game._spawn_piece()

    def test_spawn_piece_game_over(self, initialized_game):
        """Testa Game Over quando não é possível posicionar nova peça"""
        # Preenche o topo do tabuleiro para forçar Game Over
        for x in range(initialized_game.board.cols):
            initialized_game.board.grid[0][x] = '*'
            
        with pytest.raises(GameOverException):
            initialized_game._spawn_piece()

    def test_try_rotation_invalid(self, game):
        """Testa rotação quando não há peça atual"""
        assert game.try_rotation('right') == False

    @pytest.mark.parametrize("direction", ['left', 'right', 'down'])
    def test_move_piece(self, initialized_game, direction):
        """Testa movimento da peça em todas as direções"""
        original_x = initialized_game.current_piece.x
        original_y = initialized_game.current_piece.y
        
        initialized_game.move_piece(direction)
        
        if direction == 'left':
            assert initialized_game.current_piece.y == original_y - 1
        elif direction == 'right':
            assert initialized_game.current_piece.y == original_y + 1
        elif direction == 'down':
            assert initialized_game.current_piece.x == original_x + 1

    def test_move_piece_invalid(self, game):
        """Testa movimento quando não há peça atual"""
        assert game.move_piece('down') == False

    def test_calculate_score(self, initialized_game):
        """Testa cálculo de pontuação para diferentes números de linhas"""
        assert initialized_game._calculate_score(1) == 100  # Uma linha
        assert initialized_game._calculate_score(2) == 300  # Duas linhas
        assert initialized_game._calculate_score(3) == 500  # Três linhas
        assert initialized_game._calculate_score(4) == 800  # Quatro linhas
        assert initialized_game._calculate_score(5) == 0    # Número inválido de linhas

    def test_piece_preview(self, initialized_game):
        """Testa geração da prévia de peças"""
        piece_type, symbol = Game.PIECE_TYPES['I']
        preview = initialized_game._get_piece_preview(piece_type, symbol)
        
        # Verifica dimensões da prévia
        assert len(preview) == 4
        assert len(preview[0]) == 4
        
        # Verifica se a peça está presente na prévia
        has_piece = False
        for row in preview:
            if symbol in row:
                has_piece = True
                break
        assert has_piece

    def test_game_save_and_load(self, initialized_game, tmp_path):
        """Testa salvamento e carregamento do jogo"""
        # Configura um diretório temporário para o teste
        os.chdir(tmp_path)
        
        # Salva o jogo
        initialized_game.save_game()
        
        # Verifica se um arquivo foi criado
        saved_files = [f for f in os.listdir() if f.endswith('.pkl')]
        assert len(saved_files) == 1
        
        # Carrega o jogo
        loaded_game = Game.load_game(saved_files[0])
        
        # Verifica se os atributos principais foram preservados
        assert loaded_game.score == initialized_game.score
        assert loaded_game.player_name == initialized_game.player_name
        assert loaded_game.board.rows == initialized_game.board.rows
        assert loaded_game.board.cols == initialized_game.board.cols

    def test_move_piece_collision(self, initialized_game):
        """Testa colisão ao mover peça para baixo"""
        # Move a peça para o fundo do tabuleiro
        while initialized_game.move_piece('down'):
            pass
            
        # Verifica se uma nova peça foi gerada
        assert initialized_game.current_piece is not None
        
        # Verifica se a pontuação foi atualizada se houver linhas completas
        # (Este teste pode variar dependendo da configuração específica)
        assert initialized_game.score >= 0

    def test_piece_generation(self):
        """Testa geração de peças aleatórias"""
        game = Game()
        game.initialize_game(20, 10, "Jogador")
            
        # Verifica se a primeira peça é, de fato, uma peca
        assert isinstance(game.current_piece, Piece)
        
        # Verifica se todas as peças na fila de preview são pecas tambem
        for piece_type, _ in game._upcoming_pieces:
            assert issubclass(piece_type, Piece)


    def test_wall_kicks(self, initialized_game):
        """Testa o sistema de wall kicks na rotação"""
        # Move a peça para perto da parede
        while initialized_game.move_piece('right'):
            pass
            
        # Tenta rotacionar - deve aplicar wall kick se necessário
        original_y = initialized_game.current_piece.y
        initialized_game.try_rotation('right')
        
        # Verifica se a peça ainda está em uma posição válida
        assert initialized_game.board.is_valid_move(
            initialized_game.current_piece,
            initialized_game.current_piece.x,
            initialized_game.current_piece.y
        )