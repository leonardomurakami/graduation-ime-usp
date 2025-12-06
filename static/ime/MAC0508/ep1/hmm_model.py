import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple
import sys
from tqdm import tqdm
import pickle
import json

class HMMTagger:
    """
    hmm de ordem 2 para pos tagging.
    usa transicoes xy->yz, pi so conta primeira tag.
    tudo vetorizado com numpy pra ir rapido.
    """
    def __init__(self, alpha=1.0, epsilon=1e-2):
        self.alpha = alpha
        self.epsilon = epsilon
        self.tags = []
        self.tag_to_idx = {}
        self.idx_to_tag = {}
        self.vocab = set()
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.unk_token = "<DESC>"
        
        self.A = None
        self.B = None
        self.pi = None
        
        self.tag_pair_to_idx = {}
        self.idx_to_tag_pair = {}
        
        self._A_tensor = None
    
    def _get_A_tensor(self) -> np.ndarray:
        """cache do tensor A (n_tags x n_tags x n_tags) pra acelerar"""
        if self._A_tensor is None and self.A is not None:
            n_tags = len(self.tags)
            self._A_tensor = self.A.reshape(n_tags, n_tags, n_tags)
        return self._A_tensor
    
    def _invalidate_A_cache(self):
        """limpa cache quando A muda"""
        self._A_tensor = None
        
    def parse_conllu(self, filepath: str) -> List[Tuple[List[str], List[str]]]:
        """le arquivo conllu"""
        sentences = []
        current_words = []
        current_tags = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line:
                    if current_words:
                        sentences.append((current_words, current_tags))
                        current_words = []
                        current_tags = []
                    continue
                
                if line.startswith('#'):
                    continue
                
                fields = line.split('\t')
                
                if '-' in fields[0]:
                    continue
                
                word = fields[1]
                tag = fields[3]
                current_words.append(word)
                current_tags.append(tag)
        
        if current_words:
            sentences.append((current_words, current_tags))
        
        return sentences
    
    def build_vocabulary(self, train_sentences: List[Tuple[List[str], List[str]]]):
        """monta vocab e mapeamentos"""
        all_tags = set()
        for _, tags in train_sentences:
            all_tags.update(tags)
        
        self.tags = sorted(list(all_tags))
        self.tag_to_idx = {tag: i for i, tag in enumerate(self.tags)}
        self.idx_to_tag = {i: tag for i, tag in enumerate(self.tags)}
        
        self.tag_pairs = []
        for t1 in self.tags:
            for t2 in self.tags:
                self.tag_pairs.append((t1, t2))
        
        self.tag_pair_to_idx = {pair: i for i, pair in enumerate(self.tag_pairs)}
        self.idx_to_tag_pair = {i: pair for i, pair in enumerate(self.tag_pairs)}
        
        for words, _ in train_sentences:
            self.vocab.update(words)
        
        self.vocab = sorted(list(self.vocab))
        self.word_to_idx = {word: i for i, word in enumerate(self.vocab)}
        self.idx_to_word = {i: word for i, word in enumerate(self.vocab)}
    
    def initialize_model(self, train_sentences: List[Tuple[List[str], List[str]]]):
        """inicializa A, B e pi contando corpus"""
        n_tags = len(self.tags)
        n_pairs = len(self.tag_pairs)
        n_vocab = len(self.vocab)
        
        tag_count = np.zeros(n_tags)
        tag_pair_count = np.zeros(n_pairs)
        trigram_count = np.zeros((n_tags, n_tags, n_tags))
        emission_count = np.zeros((n_tags, n_vocab))
        
        for words, tags in train_sentences:
            tag_indices = [self.tag_to_idx[tag] for tag in tags]
            
            for i, (word, tag_idx) in enumerate(zip(words, tag_indices)):
                tag_count[tag_idx] += 1
                word_idx = self.word_to_idx[word]
                emission_count[tag_idx, word_idx] += 1
                
                if i >= 1:
                    prev_idx = tag_indices[i-1]
                    pair_idx = self.tag_pair_to_idx[(self.tags[prev_idx], self.tags[tag_idx])]
                    tag_pair_count[pair_idx] += 1
                
                if i >= 2:
                    trigram_count[tag_indices[i-2], tag_indices[i-1], tag_idx] += 1
        
        # pi baseado na frequencia total de cada etiqueta no corpus
        self.pi = (tag_count + self.alpha) / (tag_count.sum() + self.alpha * n_tags)
        self.pi = self.pi / self.pi.sum()
        
        self.A = np.zeros((n_pairs, n_tags))
        
        for i, (t1_name, t2_name) in enumerate(self.tag_pairs):
            t1 = self.tag_to_idx[t1_name]
            t2 = self.tag_to_idx[t2_name]
            pair_count = tag_pair_count[i]
            
            # pega linha inteira do tensor: trigram_count[t1,t2,:] -> todas transicoes t1,t2->k
            tri_counts = trigram_count[t1, t2, :]
            self.A[i, :] = (tri_counts + self.alpha) / (pair_count + self.alpha * n_tags)
        
        row_sums = self.A.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        self.A = self.A / row_sums
        
        self.B = np.zeros((n_tags, n_vocab))
        for i in range(n_tags):
            self.B[i, :] = (emission_count[i, :] + self.alpha) / (tag_count[i] + self.alpha * n_vocab)
        
        row_sums = self.B.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        self.B = self.B / row_sums
    
    def process_unknown_words(self, dev_file: str, train_sentences: List[Tuple[List[str], List[str]]]):
        """adiciona token <DESC> pro vocabulario"""
        dev_sentences = self.parse_conllu(dev_file)
        
        unknown_words = set()
        for words, _ in dev_sentences:
            for word in words:
                if word not in self.vocab:
                    unknown_words.add(word)
        
        print(f"  Palavras desconhecidas (dev): {len(unknown_words):,}")
        
        if not unknown_words:
            print()
            return
        
        self.vocab.append(self.unk_token)
        unk_idx = len(self.vocab) - 1
        self.word_to_idx[self.unk_token] = unk_idx
        self.idx_to_word[unk_idx] = self.unk_token
        
        n_tags = len(self.tags)
        new_B = np.zeros((n_tags, len(self.vocab)))
        new_B[:, :-1] = self.B
        
        # conta tags das palavras desconhecidas no corpus de validacao
        unknown_tag_counts = np.zeros(n_tags)
        total_unknown = 0
        
        for words, tags in dev_sentences:
            for word, tag in zip(words, tags):
                if word not in self.word_to_idx or word == self.unk_token:
                    tag_idx = self.tag_to_idx[tag]
                    unknown_tag_counts[tag_idx] += 1
                    total_unknown += 1
        
        new_B[:, unk_idx] = (unknown_tag_counts + self.alpha) / (total_unknown + self.alpha * n_tags)
        
        row_sums = new_B.sum(axis=1, keepdims=True)
        self.B = new_B / row_sums
        
        print(f"  Token <DESC> adicionado com {total_unknown:,} ocorrências de palavras desconhecidas no dev\n")
    
    def forward_algorithm(self, obs_seq: List[int]) -> Tuple[np.ndarray, float]:
        """algoritmo forward vetorizado"""
        T = len(obs_seq)
        n_tags = len(self.tags)
        
        alpha = np.zeros((T, n_tags, n_tags))
        
        if T == 0:
            return alpha, 0.0
        
        if T == 1:
            for i in range(n_tags):
                alpha[0, i, i] = self.pi[i] * self.B[i, obs_seq[0]]
            log_likelihood = np.log(alpha[0].sum() + 1e-10)
            return alpha, log_likelihood
        
        A_tensor = self._get_A_tensor()
        
        # inicializacao t=1: alpha[1,i,j] = pi[i] * B[i,o0] * A[i,j,j] * B[j,o1]
        pi_B0 = self.pi * self.B[:, obs_seq[0]]
        A_diag = np.einsum('ijj->ij', A_tensor)  # extrai diagonal A[i,j,j]
        B1 = self.B[:, obs_seq[1]]
        
        alpha[1] = pi_B0[:, np.newaxis] * A_diag * B1[np.newaxis, :]
        
        # recursao: soma sobre i de alpha[t-1,i,j] * A[i,j,k] * B[k,ot]
        for t in range(2, T):
            for j in range(n_tags):
                # broadcasting: alpha[t-1,:,j] (n_tags,) com A[:,j,:] (n_tags,n_tags) -> soma em i
                alpha[t, j, :] = np.sum(alpha[t-1, :, j, np.newaxis] * A_tensor[:, j, :], axis=0) * self.B[:, obs_seq[t]]
        
        log_likelihood = np.log(alpha[T-1].sum() + 1e-10)
        return alpha, log_likelihood
    
    def backward_algorithm(self, obs_seq: List[int]) -> np.ndarray:
        """algoritmo backward vetorizado"""
        T = len(obs_seq)
        n_tags = len(self.tags)
        
        beta = np.zeros((T, n_tags, n_tags))
        
        if T == 0:
            return beta
        
        if T == 1:
            beta[0, :, :] = 1.0
            return beta
        
        beta[T-1, :, :] = 1.0
        
        A_tensor = self._get_A_tensor()
        
        # recursao reversa: soma sobre k de A[i,j,k] * B[k,o_{t+1}] * beta[t+1,j,k]
        for t in range(T-2, 0, -1):
            B_next = self.B[:, obs_seq[t+1]]
            
            for i in range(n_tags):
                for j in range(n_tags):
                    beta[t, i, j] = np.sum(A_tensor[i, j, :] * B_next * beta[t+1, j, :])
        
        return beta
    
    def compute_gamma_xi(self, obs_seq: List[int], alpha: np.ndarray, 
                         beta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """calcula gamma e xi"""
        T = len(obs_seq)
        n_tags = len(self.tags)
        
        gamma = np.zeros((T, n_tags, n_tags))
        xi = np.zeros((T-1, n_tags, n_tags, n_tags))
        
        if T <= 1:
            return gamma, xi
        
        for t in range(T):
            denom = alpha[t].sum() + 1e-10
            gamma[t] = alpha[t] / denom
        
        A_tensor = self._get_A_tensor()
        
        for t in range(T-1):
            denom = alpha[t].sum() + 1e-10
            B_next = self.B[:, obs_seq[t+1]]
            
            # xi[t,i,j,k] = alpha[t,i,j] * A[i,j,k] * B[k,o_{t+1}] * beta[t+1,j,k] / Z
            for i in range(n_tags):
                for j in range(n_tags):
                    xi[t, i, j, :] = (alpha[t, i, j] * A_tensor[i, j, :] * 
                                      B_next * beta[t+1, j, :]) / denom
        
        return gamma, xi
    
    def baum_welch(self, train_sentences: List[Tuple[List[str], List[str]]]):
        """algoritmo baum-welch"""
        print(f"{'='*70}")
        print(f"{'TREINAMENTO':^70}")
        print(f"{'='*70}\n")
        
        obs_sequences = []
        for words, _ in train_sentences:
            obs_seq = []
            for word in words:
                if word in self.word_to_idx:
                    obs_seq.append(self.word_to_idx[word])
                else:
                    obs_seq.append(self.word_to_idx[self.unk_token])
            if len(obs_seq) >= 2:
                obs_sequences.append(obs_seq)
        
        n_tags = len(self.tags)
        n_pairs = len(self.tag_pairs)
        n_vocab = len(self.vocab)
        
        prev_A = self.A.copy()
        prev_B = self.B.copy()
        prev_pi = self.pi.copy()
        
        iteration = 0
        first_distance = None
        
        print(f"  Iteração | Log-Likelihood | Distância | Razão")
        print(f"  {'-'*60}")
        
        while True:
            iteration += 1
            self._invalidate_A_cache()
            
            # e-step: acumula contagens esperadas
            A_numerator = np.zeros((n_pairs, n_tags))
            A_denominator = np.zeros(n_pairs)
            B_numerator = np.zeros((n_tags, n_vocab))
            B_denominator = np.zeros(n_tags)
            pi_numerator = np.zeros(n_tags)
            
            total_log_likelihood = 0.0
            
            for obs_seq in tqdm(obs_sequences, desc=f"  Iteração {iteration}", leave=False):
                alpha, log_likelihood = self.forward_algorithm(obs_seq)
                beta = self.backward_algorithm(obs_seq)
                gamma, xi = self.compute_gamma_xi(obs_seq, alpha, beta)
                
                total_log_likelihood += log_likelihood
                
                T = len(obs_seq)
                
                pi_numerator += gamma[1, :, 0]
                
                for t in range(T-1):
                    for i in range(n_tags):
                        for j in range(n_tags):
                            pair_idx = self.tag_pair_to_idx[(self.tags[i], self.tags[j])]
                            A_numerator[pair_idx, :] += xi[t, i, j, :]
                            A_denominator[pair_idx] += gamma[t, i, j]
                
                # soma gamma[t] sobre dimensao i, depois acumula em B_numerator
                for t in range(T):
                    gamma_sum_per_tag = gamma[t].sum(axis=0)
                    B_numerator[:, obs_seq[t]] += gamma_sum_per_tag
                    B_denominator += gamma_sum_per_tag
            
            # m-step: re-estima parametros
            
            self.pi = pi_numerator + self.alpha
            self.pi = self.pi / self.pi.sum()
            
            self.A = (A_numerator + self.alpha) / (A_denominator[:, np.newaxis] + self.alpha * n_tags)
            row_sums = self.A.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            self.A = self.A / row_sums
            
            self.B = (B_numerator + self.alpha) / (B_denominator[:, np.newaxis] + self.alpha * n_vocab)
            row_sums = self.B.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            self.B = self.B / row_sums
            
            distance = (np.sum((self.A - prev_A)**2) + 
                       np.sum((self.B - prev_B)**2) + 
                       np.sum((self.pi - prev_pi)**2))
            
            if first_distance is None:
                first_distance = distance
                ratio = 1.0
            else:
                ratio = distance / first_distance
            
            print(f"  {iteration:^8} | {total_log_likelihood:^14.2f} | {distance:^9.2e} | {ratio:^9.2e}")
            
            if ratio < self.epsilon:
                print(f"\n  Convergência atingida após {iteration} iterações")
                print(f"  Distância final / Distância inicial = {ratio:.2e} < {self.epsilon}\n")
                break
            
            if iteration >= 100:
                print(f"\n  Número máximo de iterações (100) atingido\n")
                break
            
            prev_A = self.A.copy()
            prev_B = self.B.copy()
            prev_pi = self.pi.copy()
        
        print(f"{'='*70}\n")
    
    def viterbi(self, words: List[str]) -> List[str]:
        """algoritmo de viterbi pra hmm ordem 2"""
        obs_seq = []
        for word in words:
            if word in self.word_to_idx:
                obs_seq.append(self.word_to_idx[word])
            else:
                obs_seq.append(self.word_to_idx[self.unk_token])
        
        T = len(obs_seq)
        n_tags = len(self.tags)
        
        if T == 0:
            return []
        
        if T == 1:
            probs = self.pi * self.B[:, obs_seq[0]]
            return [self.tags[np.argmax(probs)]]
        
        viterbi_prob = np.zeros((T, n_tags, n_tags))
        backpointer = np.zeros((T, n_tags, n_tags), dtype=int)
        
        A_tensor = self._get_A_tensor()
        
        pi_B0 = self.pi * self.B[:, obs_seq[0]]
        A_diag = np.einsum('ijj->ij', A_tensor)
        B1 = self.B[:, obs_seq[1]]
        
        viterbi_prob[1] = pi_B0[:, np.newaxis] * A_diag * B1[np.newaxis, :]
        
        # acha max sobre i de: viterbi[t-1,i,j] * A[i,j,k] * B[k,ot]
        for t in range(2, T):
            for j in range(n_tags):
                for k in range(n_tags):
                    probs = viterbi_prob[t-1, :, j] * A_tensor[:, j, k]
                    viterbi_prob[t, j, k] = self.B[k, obs_seq[t]] * np.max(probs)
                    backpointer[t, j, k] = np.argmax(probs)
        
        best_path_prob = np.max(viterbi_prob[T-1])
        last_states = np.unravel_index(np.argmax(viterbi_prob[T-1]), viterbi_prob[T-1].shape)
        
        path = [last_states[1], last_states[0]]
        for t in range(T-1, 1, -1):
            prev_state = backpointer[t, path[-1], path[-2]]
            path.append(prev_state)
        
        path.reverse()
        
        return [self.tags[idx] for idx in path]
    
    def train(self, train_file: str, dev_file: str = None, run_baum_welch: bool = True):
        """treina o modelo"""
        train_sentences = self.parse_conllu(train_file)
        
        print(f"\n{'='*70}")
        print(f"{'TREINAMENTO':^70}")
        print(f"{'='*70}")
        print(f"\n  Sentenças de treino: {len(train_sentences):,}")
        
        self.build_vocabulary(train_sentences)
        print(f"  Número de etiquetas: {len(self.tags)}")
        print(f"  Tamanho do vocabulário: {len(self.vocab):,}")
        print(f"  Número de pares de estados: {len(self.tag_pairs)}")
        
        self.initialize_model(train_sentences)
        print(f"  Modelo inicializado com contagens + Lidstone (α={self.alpha})")
        
        print(f"\n  Verificação de normalização:")
        print(f"    Soma de π: {self.pi.sum():.6f}")
        print(f"    Somas das linhas de A: min={self.A.sum(axis=1).min():.6f}, max={self.A.sum(axis=1).max():.6f}")
        print(f"    Somas das linhas de B: min={self.B.sum(axis=1).min():.6f}, max={self.B.sum(axis=1).max():.6f}")
        print()
        
        if dev_file:
            self.process_unknown_words(dev_file, train_sentences)
        
        if run_baum_welch:
            self.baum_welch(train_sentences)
            
            print(f"  Verificação de normalização pós Baum-Welch:")
            print(f"    Soma de π: {self.pi.sum():.6f}")
            print(f"    Somas das linhas de A: min={self.A.sum(axis=1).min():.6f}, max={self.A.sum(axis=1).max():.6f}")
            print(f"    Somas das linhas de B: min={self.B.sum(axis=1).min():.6f}, max={self.B.sum(axis=1).max():.6f}")
            print()
        
        print(f"{'='*70}\n")
    
    def evaluate(self, test_file: str) -> Dict:
        """avalia no conjunto de teste"""
        test_sentences = self.parse_conllu(test_file)
        
        print(f"{'='*70}")
        print(f"{'AVALIAÇÃO NO CONJUNTO DE TESTE':^70}")
        print(f"{'='*70}")
        print(f"\n  Sentenças de teste: {len(test_sentences):,}\n")
        
        tag_stats = defaultdict(lambda: {'correct': 0, 'predicted': 0, 'gold': 0})
        total_correct = 0
        total_words = 0
        
        word_difficulty = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for words, gold_tags in tqdm(test_sentences, desc="  Etiquetando"):
            pred_tags = self.viterbi(words)
            
            for word, gold, pred in zip(words, gold_tags, pred_tags):
                total_words += 1
                word_difficulty[word]['total'] += 1
                
                if gold == pred:
                    total_correct += 1
                    tag_stats[gold]['correct'] += 1
                    word_difficulty[word]['correct'] += 1
                
                tag_stats[gold]['gold'] += 1
                tag_stats[pred]['predicted'] += 1
        
        metrics = self._calculate_metrics(tag_stats, total_correct, total_words, word_difficulty)
        
        return metrics
    
    def _calculate_metrics(self, tag_stats: Dict, total_correct: int, 
                          total_words: int, word_difficulty: Dict) -> Dict:
        """calcula metricas"""
        tag_metrics = {}
        
        for tag, stats in tag_stats.items():
            precision = stats['correct'] / stats['predicted'] if stats['predicted'] > 0 else 0
            recall = stats['correct'] / stats['gold'] if stats['gold'] > 0 else 0
            
            if precision + recall > 0:
                f1 = 2 * precision * recall / (precision + recall)
            else:
                f1 = 0
            
            tag_metrics[tag] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'correct': stats['correct'],
                'predicted': stats['predicted'],
                'gold': stats['gold']
            }
        
        avg_precision = sum(m['precision'] for m in tag_metrics.values()) / len(tag_metrics)
        avg_recall = sum(m['recall'] for m in tag_metrics.values()) / len(tag_metrics)
        avg_f1 = sum(m['f1'] for m in tag_metrics.values()) / len(tag_metrics)
        
        if avg_precision + avg_recall > 0:
            global_f1 = 2 * avg_precision * avg_recall / (avg_precision + avg_recall)
        else:
            global_f1 = 0
        
        accuracy = total_correct / total_words
        
        top_10 = sorted(tag_metrics.items(), key=lambda x: x[1]['f1'], reverse=True)[:10]
        
        bottom_10 = sorted(
            [(t, m) for t, m in tag_metrics.items() if m['f1'] > 0],
            key=lambda x: x[1]['f1']
        )[:10]
        
        word_errors = {}
        for word, stats in word_difficulty.items():
            if stats['total'] >= 3:
                error_rate = 1 - (stats['correct'] / stats['total'])
                word_errors[word] = {
                    'error_rate': error_rate,
                    'total': stats['total'],
                    'correct': stats['correct']
                }
        
        hardest_words = sorted(word_errors.items(), 
                              key=lambda x: (x[1]['error_rate'], x[1]['total']), 
                              reverse=True)[:10]
        
        return {
            'tag_metrics': tag_metrics,
            'avg_precision': avg_precision,
            'avg_recall': avg_recall,
            'avg_f1': avg_f1,
            'global_f1': global_f1,
            'accuracy': accuracy,
            'top_10_tags': top_10,
            'bottom_10_tags': bottom_10,
            'hardest_words': hardest_words,
            'total_correct': total_correct,
            'total_words': total_words
        }
    
    def print_evaluation(self, metrics: Dict):
        """imprime resultados"""
        print(f"\n{'='*70}")
        print(f"{'RESULTADOS':^70}")
        print(f"{'='*70}\n")
        
        print(f"  Métricas Globais:")
        print(f"    Acurácia:         {metrics['accuracy']:.2%}")
        print(f"    Precisão Média:   {metrics['avg_precision']:.2%}")
        print(f"    Cobertura Média:  {metrics['avg_recall']:.2%}")
        print(f"    Medida-F (média): {metrics['avg_f1']:.2%}")
        print(f"    Medida-F (global):{metrics['global_f1']:.2%}")
        print(f"    Etiquetas corretas: {metrics['total_correct']:,} / {metrics['total_words']:,}")
        
        print(f"\n  Top 10 etiquetas mais fáceis de prever:")
        print(f"  {'#':<4} {'Etiqueta':<15} {'F1':>8} {'Prec':>8} {'Cob':>8} {'Corretas':>10}")
        print(f"  {'-'*58}")
        for i, (tag, stats) in enumerate(metrics['top_10_tags'], 1):
            print(f"  {i:<4} {tag:<15} {stats['f1']:>7.2%} "
                  f"{stats['precision']:>7.2%} {stats['recall']:>7.2%} "
                  f"{stats['correct']:>10}")
        
        print(f"\n  Top 10 etiquetas mais difíceis de prever:")
        print(f"  {'#':<4} {'Etiqueta':<15} {'F1':>8} {'Prec':>8} {'Cob':>8} {'Corretas':>10}")
        print(f"  {'-'*58}")
        for i, (tag, stats) in enumerate(metrics['bottom_10_tags'], 1):
            print(f"  {i:<4} {tag:<15} {stats['f1']:>7.2%} "
                  f"{stats['precision']:>7.2%} {stats['recall']:>7.2%} "
                  f"{stats['correct']:>10}")
        
        print(f"\n  Top 10 palavras mais difíceis de etiquetar:")
        print(f"  {'#':<4} {'Palavra':<20} {'Taxa Erro':>12} {'Acertos':>10} {'Total':>8}")
        print(f"  {'-'*58}")
        for i, (word, stats) in enumerate(metrics['hardest_words'], 1):
            display_word = word[:18] + '..' if len(word) > 20 else word
            print(f"  {i:<4} {display_word:<20} {stats['error_rate']:>11.2%} "
                  f"{stats['correct']:>10} {stats['total']:>8}")
        
        print(f"\n{'='*70}\n")


def main():
    import os
    
    train_file = "pt_porttinari-ud-train.conllu"
    dev_file = "pt_porttinari-ud-dev.conllu"
    test_file = "pt_porttinari-ud-test.conllu"
    
    files_missing = []
    for f in [train_file, dev_file, test_file]:
        if not os.path.exists(f):
            files_missing.append(f)
    
    if files_missing:
        print(f"\nERRO: Os seguintes arquivos não foram encontrados:")
        for f in files_missing:
            print(f"  - {f}")
        print(f"\nBaixe os arquivos do repositório:")
        print(f"https://github.com/UniversalDependencies/UD_Portuguese-Porttinari/tree/master\n")
        return
    
    print("\n" + "="*70)
    print(f"{'EP1 - PARTE B':^70}")
    print("="*70)
    
    model = HMMTagger(alpha=1.0, epsilon=1e-2)
    model.train(train_file, dev_file, run_baum_welch=True)
    
    metrics = model.evaluate(test_file)
    
    model.print_evaluation(metrics)


if __name__ == "__main__":
    main()