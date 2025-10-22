
import glob, os

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

# Create bigrams (two characters in a row)
states = [long_text[i:i+2] for i in range(len(long_text)-1)]

os.makedirs("outputs", exist_ok=True)
out = "outputs/hmm_bigram_states.txt"

with open(out, "w", encoding="utf-8") as f:
    for st in states:
        f.write(st + "\n")

print(f"Wrote {len(states)} bigrams -> {out}")
