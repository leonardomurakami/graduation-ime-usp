"""Corpus loading and cleaning functions."""

import re
import unicodedata
from pathlib import Path

import pandas as pd
import requests


def download_corpus(url: str, output_path: Path) -> Path:
    """Download the Excel corpus file."""
    print(f"Baixando córpus de {url}...")
    
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    
    print(f"Arquivo salvo em: {output_path}")
    return output_path


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    text = unicodedata.normalize("NFC", text)
    # Remove all ASCII control characters (0-8, 11, 12, 14-31, 127-159) from the text.
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def load_and_clean_corpus(excel_path: Path) -> pd.DataFrame:
    """Load and clean the corpus from Excel file."""
    print(f"Carregando córpus de {excel_path}...")
    
    df = pd.read_excel(excel_path, engine='openpyxl')
    print(f"Colunas encontradas: {df.columns.tolist()}")
    print(f"Número de linhas original: {len(df)}")
    
    col_mapping = _detect_columns(df)
    print(f"Mapeamento de colunas: {col_mapping}")
    
    clean_df = pd.DataFrame({
        'portugues': df[col_mapping['portugues']].apply(clean_text),
        'tupi_antigo': df[col_mapping['tupi_antigo']].apply(clean_text)
    })
    
    clean_df = clean_df[
        (clean_df['portugues'].str.len() > 0) & 
        (clean_df['tupi_antigo'].str.len() > 0)
    ].drop_duplicates().reset_index(drop=True)
    
    print(f"Número de pares após limpeza: {len(clean_df)}")
    return clean_df


def _detect_columns(df: pd.DataFrame) -> dict:
    """Detect Portuguese and Tupi columns in DataFrame."""
    col_mapping = {}
    
    for col in df.columns:
        col_lower = str(col).lower()
        if 'portugu' in col_lower or 'pt' in col_lower:
            col_mapping['portugues'] = col
        elif 'tupi' in col_lower:
            col_mapping['tupi_antigo'] = col
    
    if 'portugues' not in col_mapping:
        col_mapping['portugues'] = df.columns[0]
    if 'tupi_antigo' not in col_mapping:
        for col in df.columns:
            if col != col_mapping['portugues']:
                col_mapping['tupi_antigo'] = col
                break
    
    return col_mapping

