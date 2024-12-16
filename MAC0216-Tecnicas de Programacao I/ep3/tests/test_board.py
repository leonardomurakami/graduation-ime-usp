import pytest
from src.board import Board
from src.pieces import IPiece, OPiece

class TestBoard:
    @pytest.fixture
    def empty_board(self):
        """Cria um tabuleiro 6x4 vazio para testes"""
        return Board(6, 4)
    
    def test_board_initialization(self, empty_board):
        """Testa se o tabuleiro é inicializado com dimensões corretas e células vazias"""
        assert empty_board.rows == 6
        assert empty_board.cols == 4
        assert len(empty_board.grid) == 6
        assert len(empty_board.grid[0]) == 4
        assert all(cell == ' ' for row in empty_board.grid for cell in row)

    def test_board_properties(self, empty_board):
        """Testa se as propriedades do tabuleiro retornam valores corretos"""
        assert empty_board.rows == 6
        assert empty_board.cols == 4
        assert isinstance(empty_board.grid, list)
        assert isinstance(empty_board.grid[0], list)

    @pytest.mark.parametrize("piece_config, pos_x, pos_y, expected", [
        # Movimentos válidos
        (("I", 0, 1), 0, 1, True),    # Peça I no topo (centralizada)
        (("I", 2, 1), 2, 1, True),    # Peça I no centro
        (("O", 3, 1), 3, 1, True),    # Peça O próxima à base
        
        # Movimentos inválidos - fora do tabuleiro
        (("I", 0, -1), 0, -1, False),  # Fora pela esquerda
        (("I", -1, 1), -1, 1, False),  # Fora pelo topo
        (("I", 6, 1), 6, 1, False),    # Fora pela base
        (("I", 0, 4), 0, 4, False),    # Fora pela direita
        
        # Movimentos inválidos - peça ultrapassa limites
        (("O", 5, 1), 5, 1, False),    # Peça O ultrapassa base
        (("O", 0, 3), 0, 3, False),    # Peça O ultrapassa direita
    ])
    def test_is_valid_move(self, empty_board, piece_config, pos_x, pos_y, expected):
        """Testa movimentos válidos e inválidos com diferentes configurações de peças"""
        piece_type, _, _ = piece_config
        piece = IPiece(pos_x, pos_y, '*') if piece_type == "I" else OPiece(pos_x, pos_y, '$')
        assert empty_board.is_valid_move(piece, pos_x, pos_y) == expected

    def test_is_valid_move_with_collision(self, empty_board):
        """Testa que movimentos são inválidos quando haveria sobreposição de peças"""
        # Coloca primeira peça
        piece1 = OPiece(0, 1, '$')
        empty_board.place_piece(piece1)
        
        # Tenta colocar outra peça no mesmo lugar
        piece2 = OPiece(0, 1, '$')
        assert empty_board.is_valid_move(piece2, 0, 1) == False

    def test_place_piece(self, empty_board):
        """Testa colocação de peças no tabuleiro"""
        piece = IPiece(1, 1, '*')
        empty_board.place_piece(piece)
        
        # Verifica se a peça foi colocada corretamente
        for dx, dy in piece.shape:
            assert empty_board.grid[piece.x + dx][piece.y + dy] == '*'
        
        # Verifica se outras células continuam vazias
        assert empty_board.grid[0][0] == ' '
        assert empty_board.grid[1][0] == ' '

    def test_clear_lines(self):
        """Testa o funcionamento completo da limpeza de linhas"""
        # Cria um tabuleiro maior para acomodar melhor as peças
        board = Board(8, 4)
        
        # 1. Coloca peça O no topo
        piece1 = OPiece(0, 0, '$')
        board.place_piece(piece1)
        assert board.clear_lines() == 0
        
        # 2. Preenche uma linha completa na linha 6
        piece2 = IPiece(6, 0, '*')
        piece2.rotate_right()  # Rotaciona para horizontal
        board.place_piece(piece2)
        assert board.clear_lines() == 1
        
        # 3. Verifica se a peça do topo caiu
        assert board.grid[1][0] == '$'
        assert board.grid[1][1] == '$'
        assert board.grid[2][0] == '$'
        assert board.grid[2][1] == '$'
        
        # 4. Verifica se a linha limpa está vazia
        assert all(cell == ' ' for cell in board.grid[6])

    def test_clear_lines_with_no_complete_lines(self, empty_board):
        """Testa clear_lines quando não há linhas completas"""
        piece = OPiece(0, 1, '$')
        empty_board.place_piece(piece)
        
        lines_cleared = empty_board.clear_lines()
        assert lines_cleared == 0
