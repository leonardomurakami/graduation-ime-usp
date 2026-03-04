"""Corpus analysis functions."""

import pandas as pd


def analyze_corpus(df: pd.DataFrame) -> dict:
    """Analyze corpus statistics."""
    stats = {
        'total_pairs': len(df),
        'pt_avg_chars': df['portugues'].str.len().mean(),
        'pt_avg_words': df['portugues'].str.split().str.len().mean(),
        'ta_avg_chars': df['tupi_antigo'].str.len().mean(),
        'ta_avg_words': df['tupi_antigo'].str.split().str.len().mean(),
    }
    
    print("\n" + "="*50)
    print("Estatísticas do Córpus")
    print("="*50)
    print(f"Total de pares: {stats['total_pairs']}")
    print(f"\nPortuguês:")
    print(f"  Média de caracteres: {stats['pt_avg_chars']:.1f}")
    print(f"  Média de palavras:   {stats['pt_avg_words']:.1f}")
    print(f"\nTupi Antigo:")
    print(f"  Média de caracteres: {stats['ta_avg_chars']:.1f}")
    print(f"  Média de palavras:   {stats['ta_avg_words']:.1f}")
    
    return stats

