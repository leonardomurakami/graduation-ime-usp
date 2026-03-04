"""Shared configuration for the translation project."""

from pathlib import Path
import torch

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
RESULTS_DIR = ROOT_DIR / "results"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
RANDOM_SEED = 42

CORPUS_URL = "https://github.com/CalebeRezende/oldtupi_dataset/raw/main/C%C3%B3pia%20de%20portugues-guarani-tupi%20antigo.xlsx"

# NLLB model - works for both zero-shot (with language codes) and fine-tuning
DEFAULT_MODEL = "facebook/nllb-200-distilled-600M"

# Language codes for NLLB
PT_LANG_CODE = "por_Latn"
TA_LANG_CODE = "grn_Latn"  # Guarani as proxy for Tupi Antigo (same family)
