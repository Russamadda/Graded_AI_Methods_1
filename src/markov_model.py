import argparse
import glob
import os
import sys
from collections import defaultdict, Counter
import random
from typing import Optional

# A simple word-level Markov model for text generation
class WordState:
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
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

    # Weighted choice via random.choices
    def _weighted_choice(self, counter: Counter):
        if not counter:
            return None
        items, weights = zip(*counter.items())
        return random.choices(items, weights=weights, k=1)[0]

    # Sample a starting state
    def sample_start(self):
        return self._weighted_choice(self.starts)

    # Sample the next state given the current state
    def sample_next(self, w):
        return self._weighted_choice(self.transitions.get(w, Counter()))

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


def _load_sentences(path: str):
    if os.path.isdir(path):
        sentences = []
        for fp in sorted(glob.glob(os.path.join(path, "*.txt"))):
            with open(fp, encoding="utf-8") as f:
                sentences.extend(ln.strip() for ln in f if ln.strip())
        return sentences
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="data/clean")
    parser.add_argument("--n", type=int, default=5,)
    parser.add_argument("--max-len", type=int, default=30,)
    parser.add_argument("--seed", type=int, default=None,)
    parser.add_argument("--save", default="outputs/markov_samples.txt",
)
    args = parser.parse_args(argv)

    sentences = _load_sentences(args.train)
    if not sentences:
        print(f"No sentences found in {args.train}", file=sys.stderr)
        return 1
    if len(sentences) < 150:
        print(f"Warning: only {len(sentences)} sentences found. Consider adding more training data.", file=sys.stderr)

    model = WordState(seed=args.seed)
    model.fit_from_sentences(sentences)

    generated = model.generate(n=args.n, max_len=args.max_len)
    for idx, sentence in enumerate(generated, 1):
        print(f"{idx:>2}: {sentence}")

    if args.save:
        save_dir = os.path.dirname(args.save)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        with open(args.save, "w", encoding="utf-8") as f:
            for sentence in generated:
                f.write(sentence + "\n")
        print(f"\nSaved to {args.save}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
