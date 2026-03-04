"""Evaluation module."""

from .metrics import TranslationEvaluator, MetricResults
from .analysis import analyze_examples, evaluate_all_results, save_metrics

__all__ = [
    "TranslationEvaluator",
    "MetricResults",
    "analyze_examples",
    "evaluate_all_results",
    "save_metrics",
]

