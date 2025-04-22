"""!
@file scores.py
@brief Implementação do sistema de pontuação do jogo
"""

import sqlite3
import os
from datetime import datetime
from typing import Union, List, Dict

class ScoreManager:
    """!
    @brief Gerenciador de pontuações do jogo
    
    @details Responsável por salvar e recuperar pontuações do banco de dados SQLite.
    Mantém um registro histórico das melhores pontuações dos jogadores.
    """
    
    def __init__(self, db_file: str = "tetris_scores.db"):
        """!
        @brief Inicializa o gerenciador de pontuações
        
        @param db_file Nome do arquivo do banco de dados. Padrão é "tetris_scores.db"
        """
        self.max_scores = 10
        self.db_file = db_file
    
    def _ensure_db_directory(self) -> None:
        """!
        @brief Garante que o diretório do banco de dados existe
        
        @raises sqlite3.OperationalError se não for possível criar/acessar o diretório
        """
        db_dir = os.path.dirname(self.db_file)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
            except OSError:
                raise sqlite3.OperationalError(
                    f"Cannot create or access directory: {db_dir}"
                )
    
    def _initialize_db(self) -> None:
        """!
        @brief Cria a tabela de pontuações no banco de dados se não existir
        
        @raises sqlite3.OperationalError se não for possível acessar o banco
        """
        self._ensure_db_directory()
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            conn.commit()
    
    def save_score(self, name: str, score: int) -> None:
        """!
        @brief Salva uma nova pontuação no banco de dados
        
        @param name Nome do jogador
        @param score Pontuação obtida
        @raises sqlite3.OperationalError se não for possível acessar o banco
        """
        try:
            self._initialize_db()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO scores (name, score, date) VALUES (?, ?, ?)',
                    (name, score, date)
                )
                conn.commit()
        except (sqlite3.OperationalError, OSError) as e:
            raise sqlite3.OperationalError(str(e))
    
    def get_high_scores(self) -> List[Dict[str, Union[str, int]]]:
        """!
        @brief Recupera as maiores pontuações do banco de dados
        
        @return list[dict] Lista das melhores pontuações, onde cada pontuação é um
                dicionário contendo:
                - name: Nome do jogador
                - score: Pontuação obtida
                - date: Data e hora do registro
        @raises sqlite3.OperationalError se não for possível acessar o banco
        """
        try:
            self._initialize_db()
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, score, date 
                    FROM scores 
                    ORDER BY score DESC 
                    LIMIT ?
                ''', (self.max_scores,))
                
                return [
                    {"name": name, "score": score, "date": date}
                    for name, score, date in cursor.fetchall()
                ]
        except (sqlite3.OperationalError, OSError) as e:
            raise sqlite3.OperationalError(str(e))