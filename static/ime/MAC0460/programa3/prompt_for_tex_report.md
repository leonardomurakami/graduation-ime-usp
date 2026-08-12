# Prompt para gerar relatório LaTeX do EP3

Cole o texto abaixo em outro LLM (ex: Claude, GPT, Gemini) para gerar o arquivo `.tex`:

---

## Instruções

Escreva um relatório acadêmico completo em **português brasileiro** no formato **LaTeX** (classe `article`, codificação UTF-8) descrevendo o trabalho realizado no EP3 da disciplina MAC0460/MAC5832 (DCC / IME-USP, 1º semestre de 2026). O relatório deve seguir a estrutura do enunciado (ep3.pdf) e utilizar as imagens geradas nos experimentes.

**Dados do aluno:**
- Nome: Leonardo Heidi Almeida Murakami
- NUSP: 11260186
- Curso: Bacharelado em Ciência da Computação

**Sobre uso de IA:** O enunciado diz que uso de IA geradora de código NÃO É RECOMENDADO, mas se usado, deve ser descrito quais ferramentas e como. Inclua uma seção breve mencionando que ferramentas de IA foram usadas para auxiliar na escrita do código (tab completion) e do relatório.

### Estrutura do enunciado (ep3.pdf)

O EP3 é um roteiro para praticar avaliação e seleção de modelos de machine learning usando scikit-learn. As etapas são:

1. **Treinar e avaliar um único algoritmo**
   - **Primeiro passo:** Treinar e avaliar um classificador com hiperparâmetros padrão (SVM linear no dataset digits)
   - **Segundo passo:** Tuning manual de hiperparâmetros (variar kernel e C do SVM)
   - **Terceiro passo:** Grid search com scikit-learn (grid coarse seguido de grid fino)
2. **Escolher entre múltiplos algoritmos**
   - Reservar conjunto de teste separado para avaliação não-viesada
   - Usar validação cruzada (k-fold) com partição estratificada
   - Usar a mesma partição de validação para todos os algoritmos
   - Escolher modelo final baseado no erro de validação
   - Avaliar performance final no conjunto de teste

### Estrutura esperada do relatório LaTeX

O relatório deve conter as seguintes seções:

1. **Introdução** — Descrição do objetivo do EP, do dataset utilizado (Digits: 1797 amostras, imagens 8x8, 64 features, 10 classes) e dos algoritmos avaliados (SVM, Random Forest, k-NN, Decision Tree).

2. **Metodologia** — Descrição do pipeline experimental:
   - Carregamento do dataset e visualização (Figura: `images/sample_digits.png`)
   - Divisão estratificada treino/teste (70/30)
   - Padronização das features (StandardScaler)
   - Avaliação com hiperparâmetros padrão (SVM linear, C=1.0, acurácia=97.96%) (Figura: `images/confusion_matrix_linear_svm_default.png`)
   - Grid search coarse e fino para SVM com kernel RBF
   - Comparação de múltiplos algoritmos com GridSearchCV + validação cruzada estratificada (5-fold)

3. **Resultados** — Apresentar e discutir:
   - Acurácia do SVM linear com parâmetros padrão: 97.96%
   - Resultados do grid search coarse: melhores parâmetros C=1.0, gamma=scale, kernel=rbf, CV accuracy=98.17%, test accuracy=98.33%
   - Resultados do grid search fino: C≈3.16, gamma=auto, CV accuracy=98.17%, test accuracy=98.15%
   - Tabela comparativa dos algoritmos:

   | Algoritmo        | CV Accuracy | CV Std  | Test Accuracy |
   |------------------|-------------|---------|---------------|
   | SVM (RBF)        | 0.9801      | 0.0084  | 0.9815        |
   | Random Forest    | 0.9737      | 0.0054  | 0.9667        |
   | k-NN             | 0.9682      | 0.0056  | 0.9722        |
   | Decision Tree    | 0.8497      | 0.0298  | 0.8574        |

   (Figura: `images/algorithm_comparison.png` — gráfico de barras comparando CV e test accuracy)

   - Melhor modelo: SVM (RBF) com C=10.0, gamma=0.01
   - Relatório de classificação detalhado (precision, recall, f1-score por classe)
   (Figura: `images/confusion_matrix_best_model.png` — matriz de confusão do melhor modelo)

   - Análise de exemplos classificados incorretamente
   (Figura: `images/mispredicted_examples.png` — dois exemplos de dígitos mal classificados)

4. **Discussão** — Análise crítica dos resultados:
   - Por que SVM teve o melhor desempenho
   - Por que Decision Tree teve o pior desempenho
   - Diferença entre acurácia de validação cruzada e de teste
   - Importância da padronização das features
   - Considerações sobre overfitting e o papel do conjunto de teste

5. **Conclusão** — Síntese dos achados e aprendizados

6. **Ferramentas de IA utilizadas** — Descrição breve do uso de IA (tab completion no código, auxílio na escrita do relatório)

### Imagens disponíveis (salvar na pasta `images/` ao lado do .tex)

- `images/sample_digits.png` — Amostras de dígitos do dataset
- `images/confusion_matrix_linear_svm_default.png` — Matriz de confusão do SVM linear com parâmetros padrão
- `images/algorithm_comparison.png` — Comparação de acurácia entre os algoritmos
- `images/confusion_matrix_best_model.png` — Matriz de confusão do melhor modelo (SVM RBF)
- `images/mispredicted_examples.png` — Exemplos de dígitos classificados incorretamente

### Parâmetros LaTeX

- Use `\usepackage[utf8]{inputenc}` e `\usepackage[T1]{fontenc}`
- Use `\usepackage[brazilian]{babel}`
- Use `\usepackage{graphicx}` para incluir imagens
- Use `\usepackage{booktabs}` para tabelas
- Use `\usepackage{hyperref}` para links
- Use `\usepackage{amsmath}` se necessário
- Caminho das imagens: `images/nome_do_arquivo.png`
- Título: "EP3: Avaliação e Seleção de Modelos de Aprendizado de Máquina"
- Disciplina: "MAC0460/MAC5832 — DCC / IME-USP"

### Código completo do notebook (para referência)

```python
# Cell 1 (identificação)
# Leonardo Heidi Almeida Murakami, NUSP: 11260186, Undergraduate
# Use of AI-generated code is NOT RECOMMENDED

# Cell 2 (descrição)
# MAC0460 (2026) -- EP3: Model evaluation and selection
# Dataset: Digits (8x8 images, 64 features, 10 classes)
# Algorithms: SVM, Logistic Regression, Random Forest, k-NN, Decision Tree

# Cell 3 (imports)
import os, numpy as np, matplotlib.pyplot as plt, pandas as pd, seaborn as sns
from sklearn import datasets, svm
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
os.makedirs('images', exist_ok=True)

# Cell 4 (carregamento)
digits = datasets.load_digits()
X, y = digits.data, digits.target
# X shape: (1797, 64), y shape: (1797,), 10 classes
# Class distribution: [178 182 177 183 181 182 181 179 174 180]

# Cell 5 (visualização) → images/sample_digits.png
# 2x5 grid de amostras de dígitos

# Cell 6 (divisão treino/teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
# X_train: (1257, 64), X_test: (540, 64)

# Cell 7 (padronização)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Cell 8 (SVM linear padrão)
clf = svm.SVC(kernel="linear")
clf.fit(X_train_scaled, y_train)
y_pred = clf.predict(X_test_scaled)
# Accuracy: 0.9796

# Cell 9 (matriz de confusão) → images/confusion_matrix_linear_svm_default.png

# Cell 10-12 (grid search coarse e fino)
# Coarse: C=[0.1,1,10,100], gamma=[scale,auto,0.001,0.01,0.1], kernel=rbf
# Best: C=1.0, gamma=scale, CV=0.9817, test=0.9833
# Fine: C=logspace(-1,1,5) around best_C, same gamma
# Best: C=3.16, gamma=auto, CV=0.9817, test=0.9815

# Cell 14-15 (comparação de algoritmos com GridSearchCV + StratifiedKFold 5-fold)
# SVM (RBF): C=10.0, gamma=0.01, CV=0.9801±0.0084, test=0.9815
# Random Forest: max_depth=None, n_estimators=200, CV=0.9737±0.0054, test=0.9667
# k-NN: n_neighbors=5, weights=distance, CV=0.9682±0.0056, test=0.9722
# Decision Tree: max_depth=10, min_samples_split=2, CV=0.8497±0.0298, test=0.8574

# Cell 17 (gráfico comparativo) → images/algorithm_comparison.png

# Cell 18 (melhor modelo: SVM RBF) → images/confusion_matrix_best_model.png
# Classification report:
#              precision  recall  f1-score  support
#          0       1.00     1.00      1.00       54
#          1       0.95     0.98      0.96       55
#          2       1.00     0.98      0.99       53
#          3       1.00     1.00      1.00       55
#          4       0.95     0.98      0.96       54
#          5       1.00     0.98      0.99       55
#          6       0.98     1.00      0.99       54
#          7       0.96     1.00      0.98       54
#          8       1.00     0.92      0.96       52
#          9       0.98     0.96      0.97       54
#   accuracy                         0.98      540
#  macro avg     0.98     0.98      0.98      540
#  weighted avg  0.98     0.98      0.98      540

# Cell 19 (exemplos mal classificados) → images/mispredicted_examples.png
```

Gere o arquivo `.tex` completo, pronto para compilação com `pdflatex`.
