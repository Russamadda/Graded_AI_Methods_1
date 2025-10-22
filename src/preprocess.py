import os, re, sys, glob, click, regex
from typing import List


BRACKET_PATTERNS = [
    r"\[[^\[\]]*\]",      # [ ... ]
    r"\([^\(\)]*\)",      # ( ... )
    r"\{[^\{\}]*\}",      # { ... }
    r"\<[^<>]*\>",        # < ... >
]

# Removes speaker labels like "SPEAKER NAME: ..."
SPEAKER_LINE = re.compile(r"^\s*[A-Z][A-Za-z0-9 _\.-]{1,24}\s*:\s+")

# Read text from .txt or .pdf file
def read_text_from_file(path: str) -> str:
    if path.lower().endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        chunks = []
        for page in reader.pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                pass
        return "\n".join(chunks)
    raise ValueError(f"Unsupported file: {path}")

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

# Split text into sentences
def sentence_split(text: str) -> List[str]:
    import nltk
    from nltk.tokenize import sent_tokenize
    sents = sent_tokenize(text)
    sents = [s.strip() for s in sents if len(s.strip()) > 1]
    return sents

# Command-line interface
import click
@click.command()
@click.option("--in_dir", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--out_dir", required=True, type=click.Path(file_okay=False))
@click.option("--lower/--no-lower", default=False, help="Lowercase the text before sentence splitting")
@click.option("--drop-brackets/--keep-brackets", default=True, help="Remove bracketed blocks like [..], (..), {{..}}, <..>")
def main(in_dir: str, out_dir: str, lower: bool, drop_brackets: bool):
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(in_dir, "*")))
    if not files:
        print("No files found in", in_dir)
        sys.exit(0)
    total_sents = 0
    for fp in files:
        if not (fp.lower().endswith(".txt") or fp.lower().endswith(".pdf")):
            continue
        raw = read_text_from_file(fp)
        if drop_brackets:
            raw = strip_brackets(raw)
        raw = remove_speaker_labels(raw)
        raw = normalize_spaces(raw)
        if lower:
            raw = raw.lower()
        sents = sentence_split(raw)
        total_sents += len(sents)
        out_name = os.path.splitext(os.path.basename(fp))[0] + ".txt"
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            for s in sents:
                f.write(s + "\n")
        print(f"Wrote {len(sents):>5} sentences -> {out_path}")
    print(f"Total sentences: {total_sents}")

if __name__ == "__main__":
    main()
