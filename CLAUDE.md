# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run the project: `./main.sh` (executes `python3 src/main.py`)
- Python interpreter: use `python3` — `python` is not on PATH in this environment.

## Architecture

This is an in-progress static site generator following the Boot.dev course. The intended pipeline is: parse Markdown-like inline syntax into an intermediate representation (`TextNode`), then render to HTML files served from `public/`.

- `src/textnode.py` defines the intermediate representation:
  - `TextType` (Enum) — the inline span types the generator understands (plain, bold, italic, code, link, image). Enum *values* are the human-readable label used by `__repr__` (e.g. `link`), not the Markdown delimiters.
  - `TextNode` — value object with `text`, `text_type`, and optional `url`. `__eq__` and `__repr__` are intentionally implemented for unit-test ergonomics; tests will rely on field-wise equality.
- `src/main.py` is the entry point invoked by `main.sh`. Currently a smoke-test driver.
- `public/` holds the static output (currently just a hand-written `index.html` and `styles.css`); generated HTML is expected to land here later.

There are no tests, lint config, or dependency manifest yet — the project uses only the Python standard library.
