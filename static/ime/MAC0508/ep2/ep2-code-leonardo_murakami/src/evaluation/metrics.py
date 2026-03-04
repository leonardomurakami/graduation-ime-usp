"""Translation evaluation metrics."""

from dataclasses import dataclass

import pandas as pd
from sacrebleu.metrics import BLEU, CHRF


@dataclass
class MetricResults:
    """Container for evaluation metrics."""
    bleu: float
    chrf1: float
    chrf3: float
    
    def to_dict(self) -> dict:
        return {
            "BLEU": round(self.bleu, 2),
            "chrF1": round(self.chrf1, 2),
            "chrF3": round(self.chrf3, 2),
        }


class TranslationEvaluator:
    """Evaluator for machine translation using BLEU and chrF metrics."""
    
    def __init__(self):
        self.bleu = BLEU(effective_order=True)
        self.chrf1 = CHRF(beta=1)
        self.chrf3 = CHRF(beta=3)
    
    def evaluate(self, predictions: list[str], references: list[str]) -> MetricResults:
        """Calculate all metrics for predictions vs references."""
        refs = [[r] for r in references]
        return MetricResults(
            bleu=self.bleu.corpus_score(predictions, refs).score,
            chrf1=self.chrf1.corpus_score(predictions, refs).score,
            chrf3=self.chrf3.corpus_score(predictions, refs).score,
        )
    
    def evaluate_per_sentence(
        self,
        predictions: list[str],
        references: list[str],
    ) -> pd.DataFrame:
        """Calculate metrics per sentence."""
        results = []
        for pred, ref in zip(predictions, references):
            results.append({
                "prediction": pred,
                "reference": ref,
                "bleu": self.bleu.sentence_score(pred, [ref]).score,
                "chrf1": self.chrf1.sentence_score(pred, [ref]).score,
                "chrf3": self.chrf3.sentence_score(pred, [ref]).score,
            })
        return pd.DataFrame(results)

