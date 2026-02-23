# AI & Multiagent Systems — Lecture Slides

A collection of **LaTeX Beamer** presentation slides covering topics in
**Artificial Intelligence (AI)** and **Multiagent Systems (MAS)**, including
multiagent-based simulation (MABS).

These slides are designed to be modular and reusable across different talks,
courses, and academic contexts.

---

## Repository Structure

```
.
├── talks/          # One sub-folder per talk or presentation context
│   └── <talk>/     # Entry point (main and preamble .tex files) for a specific talk
│
├── chapters/       # Modular content: chapters and sections
│   └── <topic>/    # Source files for a given topic or chapter
│
└── videos/         # (local only, not versioned) Video files for slides
```

### `talks/`

Each sub-folder defines a **standalone talk** or lecture. It typically contains
a main `.tex` file that selects and assembles the relevant chapters and sections
from the `chapters/` folder. The file `preamble.tex` also provides definitions to
be used in the document's pramble.

### `chapters/`

Contains the **modular content** of the slides, organised by topic or chapter.
Each sub-folder is self-contained and can be included in one or more talks.
Topics covered include, but are not limited to:

- Introduction to Artificial Intelligence
- Multiagent systems (MAS) fundamentals
- Multiagent-based simulation (MABS)
- Agent environments as first-class abstractions

### `videos/` *(local only)*

This folder is **not versioned** and must be created locally. It should contain
any video files referenced by the slides for in-presentation playback.

> **Note:** Add `videos/` to your `.gitignore` to avoid accidentally committing
> large media files.

### `TALK.tex`

The file `TALK.tex` in the root folder contains the specification of the talk to be generated, as well as the definition of the global properties o fthe document.

---

## Building the Slides

The slides are compiled with **LaTeX Beamer**. It is recommended to use
[AutoLaTeX](http://www.arakhne.org/autolatex) for compilation:

```bash
autolatex
```

Alternatively, compile with a standard LaTeX toolchain:

```bash
pdflatex TALK.tex
bibtex TALK
pdflatex TALK.tex
pdflatex TALK.tex
```

---

## Author

**Stéphane Galland** <stephane.galland@utbm.fr>
