
from collections import defaultdict, Counter
import random

# A simple word-level Markov model for text generation
class WordState:
    def __init__(self):
        self.starts = Counter()
        self.transitions = defaultdict(Counter)

    # Update model counts from a list of tokens
    def update_from_tokens(self, tokens):
        if not tokens:
            return
        self.starts[tokens[0]] += 1
        for a, b in zip(tokens, tokens[1:]):
            self.transitions[a][b] += 1

    # Fit model from a list of sentences
    def fit_from_sentences(self, sentences):
        for s in sentences:
            tokens = s.strip().split()
            self.update_from_tokens(tokens)

    # Sample next state based on weights
    def _weighted_choice(self, counter: Counter):
        total = sum(counter.values())
        r = random.randint(1, total)
        s = 0
        for w, c in counter.items():
            s += c
            if s >= r:
                return w

    # Sample a starting state
    def sample_start(self):
        if not self.starts:
            return None
        return self._weighted_choice(self.starts)

    # Sample the next state given the current state
    def sample_next(self, w):
        nxt = self.transitions.get(w)
        if not nxt:
            return None
        return self._weighted_choice(nxt)

    # Generate a sentence
    def generate_sentence(self, max_len=30, end_tokens=('.', '!', '?')):
        w = self.sample_start()
        if not w:
            return ""
        sent = [w]
        for _ in range(max_len - 1):
            w = self.sample_next(w)
            if not w:
                break
            sent.append(w)
            if any(sent[-1].endswith(t) for t in end_tokens):
                break
        return " ".join(sent)

    # Generate multiple sentences
    def generate(self, n=5, max_len=30):
        return [self.generate_sentence(max_len=max_len) for _ in range(n)]
