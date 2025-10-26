
import glob, os, json

# Read all cleaned sentences
sents = []
for fp in sorted(glob.glob("data/clean/*.txt")):
    with open(fp, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                sents.append(ln)

# Makes a long text from all sentences
long_text = " ".join(sents)
long_text = " ".join(long_text.split())

# Create bigrams (two characters in a row)
states = [long_text[i:i+2] for i in range(len(long_text)-1)]
unique_bigrams = sorted(set(states))
vocab = {bg: idx for idx, bg in enumerate(unique_bigrams)}

os.makedirs("outputs", exist_ok=True)
out = "outputs/hmm_bigram_states.txt"
vocab_out = "outputs/hmm_bigram_vocab.json"

with open(out, "w", encoding="utf-8") as f:
    for st in states:
        f.write(st + "\n")

with open(vocab_out, "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(states)} bigrams -> {out}")
print(f"Wrote {len(vocab)} unique bigrams -> {vocab_out}")
