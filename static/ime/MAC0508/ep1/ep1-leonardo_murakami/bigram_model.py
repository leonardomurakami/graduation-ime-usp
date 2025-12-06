from collections import defaultdict
from typing import List, Dict

class BigramModel:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.bigram_counts = defaultdict(int)
        self.unigram_counts = defaultdict(int)
        self.vocabulary = set()
        self.vocab_size = 0
        self.start_token = "<s>"
        self.end_token = "</s>"
        self.unk_token = "<DESC>"
        self.prob_cache = {}
        self.next_words = defaultdict(set)
        
    def parse_conllu(self, filepath: str) -> List[List[str]]:
        sentences = []
        current_sentence = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line:
                    if current_sentence:
                        sentences.append(current_sentence)
                        current_sentence = []
                    continue
                
                if line.startswith('#'):
                    continue
                
                fields = line.split('\t')
                
                # ignora multi-word tokens
                if '-' in fields[0]:
                    continue
                
                word = fields[1]
                current_sentence.append(word)
        
        if current_sentence:
            sentences.append(current_sentence)
        
        return sentences
    
    def train(self, train_file: str, dev_file: str = None):
        train_sentences = self.parse_conllu(train_file)
        
        print(f"\n{'='*70}")
        print(f"{'TREINAMENTO DO MODELO DE BIGRAMAS':^70}")
        print(f"{'='*70}")
        print(f"\n  Sentencas de treino: {len(train_sentences):,}")
        
        # conta bigramas e unigramas
        for sentence in train_sentences:
            words = [self.start_token] + sentence + [self.end_token]
            self.vocabulary.update(words)
            
            for i in range(len(words)):
                self.unigram_counts[words[i]] += 1
                
                if i < len(words) - 1:
                    bigram = (words[i], words[i+1])
                    self.bigram_counts[bigram] += 1
                    self.next_words[words[i]].add(words[i+1])
        
        self.vocab_size = len(self.vocabulary)
        print(f"  Tamanho do vocabulario: {self.vocab_size:,}")
        
        if dev_file:
            self._process_unknown_words(train_file, dev_file)
        
        # pre-calcula as melhores predicoes
        self._precompute_best_predictions()
        print(f"{'='*70}\n")
    
    def _process_unknown_words(self, train_file: str, dev_file: str):
        """
        identifica palavras desconhecidas no dev set e ajusta o modelo
        para lidar com elas usando o token <DESC>.
        """
        dev_sentences = self.parse_conllu(dev_file)
        
        # identifica palavras desconhecidas no dev set
        # (palavras que aparecem no dev mas nao no vocabulario de treino)
        unknown_words = set()
        for sentence in dev_sentences:
            for word in sentence:
                if word not in self.vocabulary:
                    unknown_words.add(word)
        
        print(f"  Palavras desconhecidas (dev): {len(unknown_words):,} \n")
        
        if not unknown_words:
            return
        
        # adiciona o token especial ao vocabulario
        self.vocabulary.add(self.unk_token)
        original_vocab = self.vocabulary - {self.unk_token, self.start_token, self.end_token}
        
        # re-processa o corpus de treino simulando palavras desconhecidas
        # para aprender padroes de contexto com <DESC>
        train_sentences = self.parse_conllu(train_file)
        
        for sentence in train_sentences:
            words = [self.start_token] + sentence + [self.end_token]
            
            # processa bigramas
            for i in range(len(words) - 1):
                w1 = words[i]
                w2 = words[i+1]
                
                # cria versoes com <DESC> onde palavras desconhecidas apareceriam
                w1_unk = w1
                w2_unk = w2
                
                # se a palavra nao esta no vocabulario original (exceto tokens especiais)
                # simula que seria desconhecida
                if w1 not in original_vocab and w1 not in [self.start_token, self.end_token]:
                    w1_unk = self.unk_token
                if w2 not in original_vocab and w2 not in [self.start_token, self.end_token]:
                    w2_unk = self.unk_token
                
                # adiciona bigramas com <DESC> se alguma palavra seria desconhecida
                if w1_unk == self.unk_token or w2_unk == self.unk_token:
                    bigram = (w1_unk, w2_unk)
                    self.bigram_counts[bigram] += 1
                    self.next_words[w1_unk].add(w2_unk)
                    
                    # atualiza contagem de unigrama para <DESC>
                    if w1_unk == self.unk_token:
                        self.unigram_counts[self.unk_token] += 1
        
        # atualiza tamanho do vocabulario
        self.vocab_size = len(self.vocabulary)
    
    def get_probability(self, w1: str, w2: str) -> float:
        cache_key = (w1, w2)
        if cache_key in self.prob_cache:
            return self.prob_cache[cache_key]
        
        if w1 not in self.vocabulary:
            w1 = self.unk_token
        if w2 not in self.vocabulary:
            w2 = self.unk_token
        
        bigram = (w1, w2)
        
        # suavizacao de lidstone: p(w2|w1) = (c(w1,w2) + alpha) / (c(w1) + alpha * v)
        numerator = self.bigram_counts[bigram] + self.alpha
        denominator = self.unigram_counts[w1] + self.alpha * self.vocab_size
        
        prob = numerator / denominator
        self.prob_cache[cache_key] = prob
        
        return prob
    
    def _precompute_best_predictions(self):
        """
        pre-calcula a melhor predicao para cada palavra do vocabulario.
        com suavizacao de laplace, busca apenas em palavras que ja apareceram apos w1,
        pois essas terao maior probabilidade que palavras nunca vistas apos w1.
        """
        self.best_prediction = {}
        
        for w1 in self.vocabulary:
            
            # candidatos sao palavras que ja apareceram apos w1
            candidates = self.next_words.get(w1, set())
            
            # ordena candidatos para garantir determinismo
            candidates_sorted = sorted(candidates)
            
            best_word = None
            best_prob = -1
            
            for w2 in candidates_sorted:
                prob = self.get_probability(w1, w2)
                if prob > best_prob:
                    best_prob = prob
                    best_word = w2
            
            self.best_prediction[w1] = best_word
    
    def predict_next_word(self, previous_word: str) -> str:
        if previous_word not in self.vocabulary:
            previous_word = self.unk_token
        
        return self.best_prediction.get(previous_word, self.end_token)
    
    def predict_sentence(self, sentence: List[str]) -> List[str]:
        predictions = []
        prev_word = self.start_token
        
        for true_word in sentence + [self.end_token]:
            pred_word = self.predict_next_word(prev_word)
            predictions.append(pred_word)
            prev_word = true_word if true_word in self.vocabulary else self.unk_token
        
        return predictions
    
    def evaluate(self, test_file: str) -> Dict:
        test_sentences = self.parse_conllu(test_file)
        
        print(f"{'='*70}")
        print(f"{'AVALIACAO NO CONJUNTO DE TESTE':^70}")
        print(f"{'='*70}")
        print(f"\n  Sentencas de teste: {len(test_sentences):,} \n")
        
        word_stats = defaultdict(lambda: {'correct': 0, 'predicted': 0, 'gold': 0})
        total_correct = 0
        total_words = 0
        
        for sentence in test_sentences:
            gold_words = sentence + [self.end_token]
            predicted_words = self.predict_sentence(sentence)
            
            for gold, pred in zip(gold_words, predicted_words):
                total_words += 1
                
                if gold == pred:
                    total_correct += 1
                    word_stats[gold]['correct'] += 1
                
                word_stats[gold]['gold'] += 1
                word_stats[pred]['predicted'] += 1
        
        metrics = self._calculate_metrics(word_stats, total_correct, total_words)
        
        return metrics
    
    def _calculate_metrics(self, word_stats: Dict, total_correct: int, 
                          total_words: int) -> Dict:
        word_metrics = {}
        
        for word, stats in word_stats.items():
            precision = stats['correct'] / stats['predicted'] if stats['predicted'] > 0 else 0
            recall = stats['correct'] / stats['gold'] if stats['gold'] > 0 else 0
            
            if precision + recall > 0:
                f1 = 2 * precision * recall / (precision + recall)
            else:
                f1 = 0
            
            word_metrics[word] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'correct': stats['correct'],
                'predicted': stats['predicted'],
                'gold': stats['gold']
            }
        
        avg_precision = sum(m['precision'] for m in word_metrics.values()) / len(word_metrics)
        avg_recall = sum(m['recall'] for m in word_metrics.values()) / len(word_metrics)
        avg_f1 = sum(m['f1'] for m in word_metrics.values()) / len(word_metrics)
        
        accuracy = total_correct / total_words
        
        # top 10 palavras com melhor f1
        top_10 = sorted(word_metrics.items(), key=lambda x: x[1]['f1'], reverse=True)[:10]
        
        # top 10 palavras com pior f1 (excluindo f1=0)
        bottom_10 = sorted(
            [(w, m) for w, m in word_metrics.items() if m['f1'] > 0],
            key=lambda x: x[1]['f1']
        )[:10]
        
        return {
            'word_metrics': word_metrics,
            'avg_precision': avg_precision,
            'avg_recall': avg_recall,
            'avg_f1': avg_f1,
            'accuracy': accuracy,
            'top_10_words': top_10,
            'bottom_10_words': bottom_10,
            'total_correct': total_correct,
            'total_words': total_words
        }
    
    def print_evaluation(self, metrics: Dict):
        print(f"{'='*70}")
        print(f"{'RESULTADOS':^70}")
        print(f"{'='*70}\n")
        
        print(f"  Metricas Globais:")
        print(f"    Acuracia:        {metrics['accuracy']:.2%}")
        print(f"    Precisao Media:  {metrics['avg_precision']:.2%}")
        print(f"    Cobertura Media: {metrics['avg_recall']:.2%}")
        print(f"    Medida-F Media:  {metrics['avg_f1']:.2%}")
        print(f"    Palavras corretas: {metrics['total_correct']:,} / {metrics['total_words']:,}")
        
        print(f"\n  Top 10 palavras mais faceis de prever:")
        print(f"  {'#':<4} {'Palavra':<20} {'F1':>8} {'Prec':>8} {'Cob':>8}")
        print(f"  {'-'*52}")
        for i, (word, stats) in enumerate(metrics['top_10_words'], 1):
            word_display = word if len(word) <= 18 else word[:15] + "..."
            print(f"  {i:<4} {word_display:<20} {stats['f1']:>7.2%} "
                  f"{stats['precision']:>7.2%} {stats['recall']:>7.2%}")
        
        print(f"\n  Top 10 palavras mais dificeis de prever:")
        print(f"  {'#':<4} {'Palavra':<20} {'F1':>8} {'Prec':>8} {'Cob':>8}")
        print(f"  {'-'*52}")
        for i, (word, stats) in enumerate(metrics['bottom_10_words'], 1):
            word_display = word if len(word) <= 18 else word[:15] + "..."
            print(f"  {i:<4} {word_display:<20} {stats['f1']:>7.2%} "
                  f"{stats['precision']:>7.2%} {stats['recall']:>7.2%}")
        
        print(f"\n{'='*70}\n")


def main():
    train_file = "pt_porttinari-ud-train.conllu"
    dev_file = "pt_porttinari-ud-dev.conllu"
    test_file = "pt_porttinari-ud-test.conllu"
    
    print("\n" + "="*70)
    print(f"{'EP1':^70}")
    print("="*70)
    
    # cria e treina o modelo
    model = BigramModel(alpha=1.0)
    model.train(train_file, dev_file)
    
    # avalia no conjunto de teste
    metrics = model.evaluate(test_file)
    
    # imprime resultados
    model.print_evaluation(metrics)


if __name__ == "__main__":
    main()