import os, re, sys, glob, regex
from typing import List

import nltk
for resource in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource)

BRACKET_PATTERNS = [
    r"\[[^\[\]]*\]",      # [ ... ]
    r"\([^\(\)]*\)",      # ( ... )
    r"\{[^\{\}]*\}",      # { ... }
    r"\<[^<>]*\>",        # < ... >
]

# Removes speaker labels like "SPEAKER NAME: ..."
SPEAKER_LINE = re.compile(r"^\s*[A-Z][A-Za-z0-9 _\.-]{1,24}\s*:\s+")

# --- NEW: patterns for episode markers and timestamps ---
EPISODE_PAT = re.compile(
    r"\b(?:e\.?\d{1,3}|ep\.?\d{1,3}|episode\s*\d{1,3}|s\d{1,2}e\d{1,2})\b",
    flags=re.IGNORECASE,
)
TIMESTAMP_PAT = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
PURE_NUMBER = re.compile(r"^\d+([.,]\d+)?$")

# Read text from .txt file
def read_text_from_file(path: str) -> str:
    if path.lower().endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Unsupported file (only .txt is supported): {path}")

# Remove bracketed text
def strip_brackets(text: str) -> str:
    out = text
    for pat in BRACKET_PATTERNS:
        out = regex.sub(pat, "", out)
    return out

# Remove speaker labels like "SPEAKER NAME: ..."
def remove_speaker_labels(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for ln in lines:
        cleaned.append(SPEAKER_LINE.sub("", ln))
    return "\n".join(cleaned)

# Normalize spaces and newlines
def normalize_spaces(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text

# ensure a space after sentence enders
def normalize_punctuation_spacing(text: str) -> str:
    
    return re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)

# drop episode markers and timestamps at line level
def remove_episode_and_timestamps(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        
        ln = TIMESTAMP_PAT.sub("", ln)
        
        ln = EPISODE_PAT.sub("", ln)
        lines.append(ln)
    return "\n".join(lines)

# Split text into sentences
def sentence_split(text: str) -> List[str]:
    from nltk.tokenize import sent_tokenize
    sents = sent_tokenize(text)
    # (short-sentence filter)
    sents = [s.strip() for s in sents if len(s.strip()) > 3]
    return sents

# token-level cleanup per sentence 
def clean_sentence_tokens(s: str) -> str:
    # drop pure numeric tokens and stray episode-like tokens left
    toks = s.split()
    kept = []
    for t in toks:
        if PURE_NUMBER.match(t):
            continue
        if EPISODE_PAT.search(t):
            continue
        kept.append(t)
    return " ".join(kept)

# Command-line interface
import click
@click.command()
@click.option(
    "--in_dir",
    default="data/raw",
    show_default=True,
    type=click.Path(exists=True, file_okay=False),
    
)
@click.option(
    "--out_dir",
    default="data/clean",
    show_default=True,
    type=click.Path(file_okay=False),
    
)
@click.option("--lower/--no-lower", default=True,)
@click.option("--drop-brackets/--keep-brackets", default=True,)
def main(in_dir: str, out_dir: str, lower: bool, drop_brackets: bool):
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(in_dir, "*")))
    if not files:
        print("No files found in", in_dir)
        sys.exit(0)

    total_sents = 0
    for fp in files:
        if not fp.lower().endswith(".txt"):
            # only .txt is supported
            continue

        raw = read_text_from_file(fp)
        if drop_brackets:
            raw = strip_brackets(raw)
        raw = remove_speaker_labels(raw)
        raw = normalize_spaces(raw)

        # episode/timestamp removal + punctuation spacing
        raw = remove_episode_and_timestamps(raw)
        raw = normalize_punctuation_spacing(raw)

        if lower:
            raw = raw.lower()

        sents = sentence_split(raw)

        # token-level cleanup 
        cleaned = []
        for s in sents:
            s2 = clean_sentence_tokens(s)
            # require at least 2 tokens after cleanup
            if len(s2.split()) >= 2:
                cleaned.append(s2)

        total_sents += len(cleaned)

        out_name = os.path.splitext(os.path.basename(fp))[0] + ".txt"
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            for s in cleaned:
                f.write(s + "\n")

        print(f"Wrote {len(cleaned):>5} sentences -> {out_path}")

    print(f"Total sentences: {total_sents}")

if __name__ == "__main__":
    main()
