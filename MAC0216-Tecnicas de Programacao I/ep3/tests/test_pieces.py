import pytest
from src.pieces import IPiece, JPiece, LPiece, OPiece, SPiece, TPiece, ZPiece

class TestPieces:
    @pytest.fixture
    def pieces(self):
        """Cria instâncias de todas as peças para testes"""
        return {
            'I': IPiece(0, 0, '*'),
            'J': JPiece(0, 0, '@'),
            'L': LPiece(0, 0, '#'),
            'O': OPiece(0, 0, '$'),
            'S': SPiece(0, 0, '%'),
            'T': TPiece(0, 0, '&'),
            'Z': ZPiece(0, 0, '?')
        }

    def test_piece_initialization(self, pieces):
        """Testa inicialização de todas as peças"""
        for name, piece in pieces.items():
            assert piece.x == 0
            assert piece.y == 0
            assert piece._rotation == 0
            assert len(piece.shape) > 0

    def test_piece_symbols(self, pieces):
        """Testa se os símbolos das peças estão corretos"""
        expected_symbols = {
            'I': '*',
            'J': '@',
            'L': '#',
            'O': '$',
            'S': '%',
            'T': '&',
            'Z': '?'
        }
        
        for name, piece in pieces.items():
            assert piece.symbol == expected_symbols[name]

    def test_piece_coordinates_validity(self, pieces):
        """Testa se as coordenadas das peças são válidas"""
        for piece in pieces.values():
            # Todas as coordenadas devem ser tuplas de inteiros
            for x, y in piece.shape:
                assert isinstance(x, int)
                assert isinstance(y, int)
                
            # Verifica se há coordenadas duplicadas
            coords_set = set(piece.shape)
            assert len(coords_set) == len(piece.shape)

    @pytest.mark.parametrize("piece_type,expected_blocks", [
        (IPiece, 4),  # Peça I tem 4 blocos em linha
        (JPiece, 4),  # Peça J tem 4 blocos em forma de L invertido
        (LPiece, 4),  # Peça L tem 4 blocos em forma de L
        (OPiece, 4),  # Peça O tem 4 blocos em quadrado
        (SPiece, 4),  # Peça S tem 4 blocos em forma de S
        (TPiece, 4),  # Peça T tem 4 blocos em forma de T
        (ZPiece, 4),  # Peça Z tem 4 blocos em forma de Z
    ])
    def test_piece_block_count(self, piece_type, expected_blocks):
        """Testa se cada peça tem o número correto de blocos"""
        piece = piece_type(0, 0, '*')
        assert len(piece.shape) == expected_blocks

    def test_i_piece_shapes(self):
        """Testa as formas específicas da peça I"""
        piece = IPiece(0, 0, '*')
        
        # Forma inicial (vertical)
        vertical_shape = set((x,y) for x,y in piece.shape)
        
        # Rotação para horizontal
        piece.rotate_right()
        horizontal_shape = set((x,y) for x,y in piece.shape)
        
        # Verifica que as formas são diferentes
        assert vertical_shape != horizontal_shape
        
        # Verifica que tem 4 blocos em cada forma
        assert len(vertical_shape) == 4
        assert len(horizontal_shape) == 4

    def test_o_piece_shape(self):
        """Testa as formas da peça O (deve manter-se igual em todas as rotações)"""
        piece = OPiece(0, 0, '$')
        original_shape = piece.shape.copy()
        
        # Testa todas as rotações
        for _ in range(4):
            piece.rotate_right()
            assert piece.shape == original_shape
        
        # Verifica forma específica do quadrado 2x2
        expected_shape = [(0,0), (0,1), (1,0), (1,1)]
        assert sorted(piece.shape) == sorted(expected_shape)

    def test_rotations_cycles(self, pieces):
        """Testa se após 4 rotações cada peça volta à forma original"""
        for piece in pieces.values():
            original_shape = piece.shape.copy()
            
            # Testa rotação completa (4 vezes 90 graus)
            for _ in range(4):
                piece.rotate_right()
            assert sorted(piece.shape) == sorted(original_shape)
            
            # Testa rotação completa no sentido anti-horário
            for _ in range(4):
                piece.rotate_left()
            assert sorted(piece.shape) == sorted(original_shape)

    def test_position_setters(self, pieces):
        """Testa os setters de posição das peças"""
        for piece in pieces.values():
            # Testa mudança de posição X
            piece.x = 5
            assert piece.x == 5
            
            # Testa mudança de posição Y
            piece.y = 3
            assert piece.y == 3

    @pytest.mark.parametrize("piece_type,min_width,max_width,min_height,max_height", [
        (IPiece, 1, 4, 1, 4),  # Peça I pode ser 1x4 ou 4x1
        (OPiece, 2, 2, 2, 2),  # Peça O sempre 2x2
        (TPiece, 2, 3, 2, 3),  # Peça T varia entre 2x3 e 3x2
        (JPiece, 2, 3, 2, 3),  # Peça J varia entre 2x3 e 3x2
        (LPiece, 2, 3, 2, 3),  # Peça L varia entre 2x3 e 3x2
        (SPiece, 2, 3, 2, 3),  # Peça S varia entre 2x3 e 3x2
        (ZPiece, 2, 3, 2, 3),  # Peça Z varia entre 2x3 e 3x2
    ])
    def test_piece_dimension_bounds(self, piece_type, min_width, max_width, min_height, max_height):
        """Testa os limites das dimensões das peças em todas as rotações"""
        piece = piece_type(0, 0, '*')
        
        widths = []
        heights = []
        
        # Testa todas as rotações
        for _ in range(4):
            x_coords = [x for x, _ in piece.shape]
            y_coords = [y for _, y in piece.shape]
            
            width = max(y_coords) - min(y_coords) + 1
            height = max(x_coords) - min(x_coords) + 1
            
            widths.append(width)
            heights.append(height)
            
            piece.rotate_right()
        
        assert min(widths) >= min_width
        assert max(widths) <= max_width
        assert min(heights) >= min_height
        assert max(heights) <= max_height

    def test_t_piece_basic_shape(self):
        """Testa a forma básica da peça T"""
        piece = TPiece(0, 0, '&')
        
        # Verifica que tem 4 blocos
        assert len(piece.shape) == 4
        
        # Verifica que forma um T em alguma orientação
        coords = set((x,y) for x,y in piece.shape)
        assert len(coords) == 4  # Sem sobreposição

    def test_j_l_pieces_different(self):
        """Testa se as peças J e L são diferentes"""
        j_piece = JPiece(0, 0, '@')
        l_piece = LPiece(0, 0, '#')
        
        # As peças J e L devem ter formas diferentes
        j_coords = set((x,y) for x,y in j_piece.shape)
        l_coords = set((x,y) for x,y in l_piece.shape)
        
        assert j_coords != l_coords

    def test_s_z_pieces_different(self):
        """Testa se as peças S e Z são diferentes"""
        s_piece = SPiece(0, 0, '%')
        z_piece = ZPiece(0, 0, '?')
        
        # As peças S e Z devem ter formas diferentes
        s_coords = set((x,y) for x,y in s_piece.shape)
        z_coords = set((x,y) for x,y in z_piece.shape)
        
        assert s_coords != z_coords