
import os, glob, datetime, time, random
from pathlib import Path
from typing import List, Tuple

# Markov model implementation
from markov_model import WordState

# Matrix UI libraries
from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich import box
from rich.live import Live
import pyfiglet


colorama_init()
console = Console()
MATRIX_GREEN = "bright_green"

# Project root, regardless of execution path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLEAN = PROJECT_ROOT / "data" / "clean"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


MATRIX_CHARSET = "01abcdefghijklmnopqrstuvwxyz#$%&*@"

# Aesthetics for matrix mode
def matrix_title():
    title = pyfiglet.figlet_format("MARKOV", font="slant")
    console.print(Text(title, style=MATRIX_GREEN))
    console.print(Text("super simple generator — matrix mode", style=MATRIX_GREEN))
    console.rule(Text(" ", style=MATRIX_GREEN), style=MATRIX_GREEN)

def matrix_rain(duration: float = 1.0, width: int = 72, height: int = 18,
                charset: str = MATRIX_CHARSET):
    """Quick 'rain' splash."""
    cols = width
    end = time.time() + duration
    console.clear()
    while time.time() < end:
        lines = []
        for _ in range(height):
            line = []
            for _ in range(cols):
                ch = random.choice(charset)
                line.append(f"[{MATRIX_GREEN}]{ch}[/]")
            lines.append("".join(line))
        console.print("\n".join(lines))
        time.sleep(0.06)
        console.clear()

# Data loading and model training
def read_clean_sentences(clean_dir: Path) -> List[str]:
    files = sorted((clean_dir).glob("*.txt"))
    sents: List[str] = []
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8", errors="ignore") as f:
                for ln in f:
                    ln = ln.strip()
                    if ln:
                        sents.append(ln)
        except Exception:

            pass
    return sents

# Train a Markov model from cleaned sentences
def train_model(clean_dir: Path) -> Tuple[WordState, int]:
    sents = read_clean_sentences(clean_dir)
    if not sents:
        raise FileNotFoundError(f"[ERROR] no sentences found in {clean_dir}")
    m = WordState()
    m.fit_from_sentences(sents)
    return m, len(sents)

# Ensure outputs directory exists
def ensure_outputs():
    OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

# Settings panel display
def settings_panel(clean_dir: Path, num_to_generate: int, auto_save: bool,
                   matrix_reveal: bool, reveal_speed: float, reveal_cycles: int):
    t = Table.grid(expand=True)
    t.add_row(Text("1", style=MATRIX_GREEN), Text(f"Training path: {clean_dir}", style=MATRIX_GREEN))
    t.add_row(Text("2", style=MATRIX_GREEN), Text(f"# sentences: {num_to_generate}", style=MATRIX_GREEN))
    t.add_row(Text("3", style=MATRIX_GREEN), Text(f"Auto-save: {'ON' if auto_save else 'OFF'}", style=MATRIX_GREEN))
    t.add_row(Text("4", style=MATRIX_GREEN), Text(f"Matrix reveal: {'ON' if matrix_reveal else 'OFF'}", style=MATRIX_GREEN))
    t.add_row(Text("5", style=MATRIX_GREEN), Text(f"Reveal speed: {reveal_speed:.3f}s (lower = faster)", style=MATRIX_GREEN))
    t.add_row(Text("6", style=MATRIX_GREEN), Text(f"Reveal cycles per word: {reveal_cycles}", style=MATRIX_GREEN))
    console.print(Panel(t, title="[bright_green]Settings[/]", border_style=MATRIX_GREEN, box=box.SQUARE))

def prompt_for_folder(default_path: Path) -> Path:
    entered = Prompt.ask(Text("Enter path to folder with .txt files", style=MATRIX_GREEN),
                         default=str(default_path))
    p = Path(entered).expanduser().resolve()
    return p

# Animation helpers
def _scramble(n: int) -> str:
    return "".join(random.choice(MATRIX_CHARSET) for _ in range(n))

def animate_matrix_reveal(line: str, title="Result", speed: float = 0.03, cycles: int = 10):
    """
    Reveal a full sentence word-by-word. Each word flickers with random glyphs
    for `cycles` steps before locking into the true word.
    """
    words = line.split()
    shown_prefix = ""
    with Live(Panel("", title=f"[bright_green]{title}[/]", border_style=MATRIX_GREEN, box=box.SQUARE),
              refresh_per_second=60, console=console) as live:
        for idx, w in enumerate(words):
            
            for _ in range(cycles):
                gib = _scramble(len(w))
                rendered = shown_prefix + gib + (" " if idx < len(words) - 1 else "")
                live.update(Panel(Text(rendered, style=MATRIX_GREEN),
                                  title=f"[bright_green]{title}[/]",
                                  border_style=MATRIX_GREEN, box=box.SQUARE))
                time.sleep(speed)
            
            shown_prefix += w + (" " if idx < len(words) - 1 else "")
            live.update(Panel(Text(shown_prefix, style=MATRIX_GREEN),
                              title=f"[bright_green]{title}[/]",
                              border_style=MATRIX_GREEN, box=box.SQUARE))
            time.sleep(speed * 1.5)

# Main application loop
def main():
    ensure_outputs()
    console.clear()
    matrix_rain(1.0)
    matrix_title()

    # default settings
    clean_dir = DEFAULT_CLEAN
    num_to_generate = 5
    auto_save = False
    matrix_reveal = True
    reveal_speed = 0.009
    reveal_cycles = 10

    # initial model training
    try:
        with console.status("[bright_green]training model...", spinner="dots"):
            model, n = train_model(clean_dir)
        console.print(Panel(f"[bright_green]Loaded {n} sentences from [u]{clean_dir}[/u]. Model ready.",
                            border_style=MATRIX_GREEN, box=box.SQUARE))
    except FileNotFoundError as e:
        console.print(Text(str(e), style="red"))
        new_dir = prompt_for_folder(DEFAULT_CLEAN)
        with console.status("[bright_green]training model...", spinner="dots"):
            model, n = train_model(new_dir)
        clean_dir = new_dir
        console.print(Panel(f"[bright_green]Loaded {n} sentences from [u]{clean_dir}[/u]. Model ready.",
                            border_style=MATRIX_GREEN, box=box.SQUARE))

    console.print(Text("\nPress [enter] to generate • type [s] for settings • type [q] to quit\n",
                       style=MATRIX_GREEN))

    while True:
        cmd = Prompt.ask(Text("", style=MATRIX_GREEN), default="").strip().lower()

        if cmd == "q":
            console.print(Text("exiting…", style=MATRIX_GREEN))
            break

        if cmd == "s":
            settings_panel(clean_dir, num_to_generate, auto_save,
                           matrix_reveal, reveal_speed, reveal_cycles)
            choice = Prompt.ask(Text("Change which (1/2/3/4/5/6)? [enter=cancel]",
                                     style=MATRIX_GREEN), default="")
            if choice == "1":
                new_path = prompt_for_folder(clean_dir)
                try:
                    console.print(Text("retraining…", style=MATRIX_GREEN))
                    with console.status("[bright_green]training model...", spinner="dots"):
                        model, n = train_model(new_path)
                    clean_dir = new_path
                    console.print(Text(f"ok, {n} sentences", style=MATRIX_GREEN))
                except FileNotFoundError as e:
                    console.print(Text(str(e), style="red"))
            elif choice == "2":
                val = Prompt.ask(Text("How many sentences to generate?", style=MATRIX_GREEN),
                                 default=str(num_to_generate))
                try:
                    num_to_generate = max(1, int(val))
                except ValueError:
                    console.print(Text("invalid number; keeping previous", style="red"))
            elif choice == "3":
                auto_save = not auto_save
                console.print(Text(f"Auto-save is now {'ON' if auto_save else 'OFF'}", style=MATRIX_GREEN))
            elif choice == "4":
                matrix_reveal = not matrix_reveal
                console.print(Text(f"Matrix reveal is now {'ON' if matrix_reveal else 'OFF'}", style=MATRIX_GREEN))
            elif choice == "5":
                val = Prompt.ask(Text("Reveal speed in seconds (e.g. 0.02 = faster)", style=MATRIX_GREEN),
                                 default=f"{reveal_speed:.3f}")
                try:
                    reveal_speed = max(0.005, float(val))
                except ValueError:
                    console.print(Text("invalid number; keeping previous", style="red"))
            elif choice == "6":
                val = Prompt.ask(Text("Reveal cycles per word (e.g. 8–12)", style=MATRIX_GREEN),
                                 default=str(reveal_cycles))
                try:
                    reveal_cycles = max(1, int(val))
                except ValueError:
                    console.print(Text("invalid number; keeping previous", style="red"))
            else:
                console.print(Text("no change", style=MATRIX_GREEN))
            continue

        # default: generate samples
        def to_text(sample):
            if sample is None:
                return ""
            if isinstance(sample, (list, tuple)):
                return " ".join(map(str, sample))
            return str(sample)

        raw_samples = [model.generate(max_len=28) for _ in range(num_to_generate)]
        samples = [to_text(s) for s in raw_samples]

        if matrix_reveal:
            for i, line in enumerate(samples, 1):
                animate_matrix_reveal(line, title=f"Result #{i}",
                                      speed=reveal_speed, cycles=reveal_cycles)
        else:
            out = "\n".join(samples)
            console.print(Panel(out, title="[bright_green]Result[/]", border_style=MATRIX_GREEN, box=box.SQUARE))

        if auto_save:
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            out_path = OUTPUTS_DIR / f"samples_{ts}.txt"
            with out_path.open("w", encoding="utf-8") as f:
                for s in samples:
                    f.write(s + "\n")
            console.print(Text(f"saved → {out_path}", style=MATRIX_GREEN))

        console.print(Text("\n[enter]=generate again • [s]=settings • [q]=quit", style=MATRIX_GREEN))

if __name__ == "__main__":
    main()
