# Comparação de Métricas

| Experimento   | Modelo                           | Direção   |    BLEU |   chrF1 |   chrF3 |
|:--------------|:---------------------------------|:----------|--------:|--------:|--------:|
| few-shot      | facebook/nllb-200-distilled-600M | PT→TA     | 27.5161 | 32.8315 | 42.0959 |
| few-shot      | facebook/nllb-200-distilled-600M | TA→PT     | 50      | 49.1169 | 50.6332 |
| zero-shot     | facebook/nllb-200-distilled-600M | PT→TA     |  5.5224 | 13.4269 | 16.7506 |
| zero-shot     | facebook/nllb-200-distilled-600M | TA→PT     | 45.1801 | 30.5307 | 22.1526 |