# Slides

Personal tooling for meeting slides; not part of the experiment code.

```
slides/
  scripts/
    deck.py                    helpers: start from the template in files/ (keeps its theme and layouts),
                               add title, text, table and figure slides
  decks/
    <date>_<topic>.pptx        finished decks
```

New deck: a short script that uses `deck.py`, run from the repo root:

```python
import sys; sys.path.insert(0, "slides/scripts")
from deck import ROOT, new_deck, slide, title_slide

prs = new_deck()
title_slide(prs, "AI Alignment paper: <topic>", "<dd.mm.yyyy>")
slide(prs, "<title>", ["<bullet>", (1, "<sub-bullet>")], figure="outputs/compare_models/figures/abstention_by_model.png")
prs.save(ROOT / "slides/decks/<date>_<topic>.pptx")
```

Needs python-pptx (in the main `requirements.txt`). Figures come from `outputs/compare_models/figures/`. Check the result
visually: with `layout="below"`, bullets that wrap to a second line run under the figure.
