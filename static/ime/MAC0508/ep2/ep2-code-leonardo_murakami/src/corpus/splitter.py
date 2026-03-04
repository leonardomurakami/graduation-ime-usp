"""Corpus splitting functions."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def split_corpus(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split corpus into train, validation, and test sets."""
    train_val_df, test_df = train_test_split(
        df, test_size=test_ratio, random_state=random_seed
    )
    
    val_adjusted_ratio = val_ratio / (train_ratio + val_ratio)
    train_df, val_df = train_test_split(
        train_val_df, test_size=val_adjusted_ratio, random_state=random_seed
    )
    
    print(f"\nDivisão do córpus:")
    print(f"  Treino:     {len(train_df):5d} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Validação:  {len(val_df):5d} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Teste:      {len(test_df):5d} ({len(test_df)/len(df)*100:.1f}%)")
    
    return train_df, val_df, test_df


def save_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: Path
) -> None:
    """Save corpus splits to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train_df.to_csv(output_dir / "train.csv", index=False)
    val_df.to_csv(output_dir / "val.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)
    
    print(f"\nArquivos salvos em {output_dir}:")
    print(f"  - train.csv ({len(train_df)} pares)")
    print(f"  - val.csv ({len(val_df)} pares)")
    print(f"  - test.csv ({len(test_df)} pares)")

