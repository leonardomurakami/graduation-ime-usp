"""Translation module."""

from .zero_shot import ZeroShotTranslator
from .few_shot import FewShotTrainer, TrainingConfig

__all__ = ["ZeroShotTranslator", "FewShotTrainer", "TrainingConfig"]

