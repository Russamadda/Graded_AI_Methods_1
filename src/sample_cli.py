
import os, glob, argparse
from markov_model import WordState

# Read all cleaned sentences from a directory
def read_clean_sentences(clean_dir):
    sents = []
    for fp in sorted(glob.glob(os.path.join(clean_dir, "*.txt"))):
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    sents.append(line)
    return sents

# Main function for CLI usage
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean_dir", required=True)
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--max_len", type=int, default=28)
    ap.add_argument("--save", default="outputs/samples.txt")
    args = ap.parse_args()
    
    # Read cleaned sentences
    sents = read_clean_sentences(args.clean_dir)
    if len(sents) < 150:
        print(f"Warning: only {len(sents)} sentences found.")
    model = WordState()
    model.fit_from_sentences(sents)
    samples = model.generate(n=args.num, max_len=args.max_len)
    
    # Save samples to file
    os.makedirs(os.path.dirname(args.save), exist_ok=True)
    with open(args.save, "w", encoding="utf-8") as f:
        for s in samples:
            print(s)
            f.write(s + "\n")
    print(f"\nSaved to {args.save}")


if __name__ == "__main__":
    main()
