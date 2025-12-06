"""Results analysis functions."""

import json
from pathlib import Path

import pandas as pd

from ..config import RESULTS_DIR
from .metrics import TranslationEvaluator


def load_results(results_file: Path) -> dict:
    """Load translation results from JSON file."""
    with open(results_file, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_all_results(results_dir: Path = RESULTS_DIR) -> pd.DataFrame:
    """Evaluate all result files in directory."""
    evaluator = TranslationEvaluator()
    all_results = []
    
    for results_file in results_dir.glob("*.json"):
        if "metrics" in results_file.name:
            continue
        
        print(f"\nProcessando: {results_file.name}")
        data = load_results(results_file)
        
        if "zero_shot" in results_file.name:
            experiment_type = "zero-shot"
        elif "few_shot" in results_file.name:
            experiment_type = "few-shot"
        else:
            experiment_type = "unknown"
        
        model = data.get("model", "unknown")
        
        for direction in ["pt_to_ta", "ta_to_pt"]:
            if direction not in data:
                continue
            
            dir_data = data[direction]
            metrics = evaluator.evaluate(dir_data["predictions"], dir_data["references"])
            
            all_results.append({
                "Experimento": experiment_type,
                "Modelo": model,
                "Direção": "PT→TA" if direction == "pt_to_ta" else "TA→PT",
                "BLEU": metrics.bleu,
                "chrF1": metrics.chrf1,
                "chrF3": metrics.chrf3,
            })
            
            print(f"  {direction}: BLEU={metrics.bleu:.2f}, chrF1={metrics.chrf1:.2f}, chrF3={metrics.chrf3:.2f}")
    
    return pd.DataFrame(all_results)


def analyze_examples(results_file: Path, n_good: int = 5, n_bad: int = 5) -> dict[str, pd.DataFrame]:
    """Analyze best and worst translation examples."""
    evaluator = TranslationEvaluator()
    data = load_results(results_file)
    analysis = {}
    
    for direction in ["pt_to_ta", "ta_to_pt"]:
        if direction not in data:
            continue
        
        dir_data = data[direction]
        sentence_df = evaluator.evaluate_per_sentence(
            dir_data["predictions"],
            dir_data["references"]
        )
        sentence_df["source"] = dir_data["sources"]
        sentence_df = sentence_df.sort_values("bleu", ascending=False)
        
        analysis[f"{direction}_good"] = sentence_df.head(n_good).copy()
        analysis[f"{direction}_bad"] = sentence_df.tail(n_bad).copy()
    
    return analysis


def save_metrics(df: pd.DataFrame, output_dir: Path = RESULTS_DIR) -> None:
    """Save metrics in multiple formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_dir / "metrics_comparison.csv", index=False)
    df.to_json(output_dir / "metrics_comparison.json", orient="records", indent=2, force_ascii=False)
    
    with open(output_dir / "metrics_comparison.md", "w", encoding="utf-8") as f:
        f.write("# Comparação de Métricas\n\n")
        f.write(df.to_markdown(index=False))
    
    print(f"Métricas salvas em {output_dir}")

