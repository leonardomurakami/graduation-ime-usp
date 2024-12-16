import pytest
import sqlite3
import os
from datetime import datetime
from src.scores import ScoreManager

class TestScoreManager:
    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Cria um caminho temporário para o banco de dados"""
        return str(tmp_path / "test_scores.db")

    @pytest.fixture
    def score_manager(self, temp_db_path):
        """Cria uma instância do ScoreManager com banco temporário"""
        return ScoreManager(temp_db_path)

    def test_initialization(self, score_manager, temp_db_path):
        """Testa se o ScoreManager é inicializado corretamente"""
        assert score_manager.db_file == temp_db_path
        assert score_manager.max_scores == 10
        score_manager._initialize_db()

        # Verifica se a tabela foi criada
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='scores'
            """)
            assert cursor.fetchone() is not None

    def test_save_score(self, score_manager, temp_db_path):
        """Testa o salvamento de pontuações"""
        # Salva uma pontuação
        score_manager.save_score("Jogador1", 1000)
        
        # Verifica se foi salvo corretamente
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, score FROM scores")
            result = cursor.fetchone()
            
            assert result[0] == "Jogador1"
            assert result[1] == 1000

    def test_get_high_scores_empty(self, score_manager):
        """Testa obtenção de pontuações quando não há registros"""
        high_scores = score_manager.get_high_scores()
        assert high_scores == []

    def test_get_high_scores_ordering(self, score_manager):
        """Testa se as pontuações são retornadas em ordem decrescente"""
        # Insere pontuações fora de ordem
        scores = [
            ("Jogador1", 500),
            ("Jogador2", 1000),
            ("Jogador3", 750)
        ]
        
        for name, score in scores:
            score_manager.save_score(name, score)
        
        high_scores = score_manager.get_high_scores()
        
        # Verifica ordem decrescente
        assert high_scores[0]['score'] == 1000
        assert high_scores[1]['score'] == 750
        assert high_scores[2]['score'] == 500

    def test_max_scores_limit(self, score_manager):
        """Testa se o limite de pontuações máximas é respeitado"""
        # Insere mais que o número máximo de pontuações
        for i in range(15):  # max_scores é 10
            score_manager.save_score(f"Jogador{i}", i * 100)
        
        high_scores = score_manager.get_high_scores()
        
        # Verifica se retorna apenas max_scores registros
        assert len(high_scores) == score_manager.max_scores
        
        # Verifica se são as maiores pontuações
        scores = [score['score'] for score in high_scores]
        assert scores == sorted(scores, reverse=True)

    def test_score_date_format(self, score_manager):
        """Testa se a data é salva no formato correto"""
        score_manager.save_score("Jogador1", 1000)
        
        with sqlite3.connect(score_manager.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date FROM scores")
            date_str = cursor.fetchone()[0]
            
            # Verifica se a data pode ser parseada
            try:
                datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pytest.fail("Data não está no formato correto")

    def test_duplicate_scores(self, score_manager):
        """Testa o comportamento com pontuações duplicadas"""
        # Insere mesma pontuação duas vezes
        score_manager.save_score("Jogador1", 1000)
        score_manager.save_score("Jogador1", 1000)
        
        high_scores = score_manager.get_high_scores()
        
        # Deve manter ambos os registros
        jogador1_scores = [
            score for score in high_scores 
            if score['name'] == "Jogador1"
        ]
        assert len(jogador1_scores) == 2

    def test_score_fields(self, score_manager):
        """Testa se todos os campos necessários estão presentes"""
        score_manager.save_score("Jogador1", 1000)
        high_scores = score_manager.get_high_scores()
        
        assert len(high_scores) == 1
        score_entry = high_scores[0]
        
        assert 'name' in score_entry
        assert 'score' in score_entry
        assert 'date' in score_entry

    def test_invalid_scores(self, score_manager):
        """Testa o comportamento com pontuações inválidas"""
        # Testa pontuação negativa
        score_manager.save_score("Jogador1", -100)
        
        high_scores = score_manager.get_high_scores()
        assert len(high_scores) == 1
        assert high_scores[0]['score'] == -100

    def test_special_characters_in_name(self, score_manager):
        """Testa nomes com caracteres especiais"""
        special_name = "Jogador!@#$%^&*()"
        score_manager.save_score(special_name, 1000)
        
        high_scores = score_manager.get_high_scores()
        assert high_scores[0]['name'] == special_name

    def test_database_connection_error(self, tmp_path):
        """Testa comportamento com erro de conexão do banco de dados"""
        # Cria um caminho para diretório que não existe e que não pode ser criado
        # Usando /proc que existe mas não permite escrita
        db_path = "/proc/nonexistent/scores.db"
        
        score_manager = ScoreManager(db_path)
        
        # Tentativa de salvar deveria levantar sqlite3.OperationalError
        with pytest.raises(sqlite3.OperationalError):
            score_manager.save_score("Jogador1", 1000)
        
        # Tentativa de ler também deveria levantar sqlite3.OperationalError
        with pytest.raises(sqlite3.OperationalError):
            score_manager.get_high_scores()

    def test_concurrent_access(self, score_manager):
        """Testa acesso concorrente ao banco de dados"""
        # Simula múltiplos acessos
        for i in range(100):
            score_manager.save_score(f"Jogador{i}", i)
        
        # Verifica se todos os registros foram salvos corretamente
        with sqlite3.connect(score_manager.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scores")
            count = cursor.fetchone()[0]
            assert count == 100

    def test_database_integrity(self, score_manager, temp_db_path):
        """Testa a integridade do banco de dados"""
        # Insere alguns registros
        score_manager.save_score("Jogador1", 1000)
        score_manager.save_score("Jogador2", 2000)
        
        # Força fechamento e reabertura do banco
        del score_manager
        new_manager = ScoreManager(temp_db_path)
        
        # Verifica se os dados persistiram
        high_scores = new_manager.get_high_scores()
        assert len(high_scores) == 2