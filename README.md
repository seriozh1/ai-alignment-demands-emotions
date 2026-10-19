# AI alignment demands emotions: empirical study

Empirical support for a position paper on the underdetermination of emotions and epistemic humility in AI.

**Question:** do a model's confidence and its willingness to abstain reflect whether it has the evidence humans need
to infer emotions? For example, when the answer depends on a face, does a transcript-only model abstain more than one
given the video?

**Setup:** [MoMentS](https://github.com/villacu/MoMentS) (short films with multiple-choice theory-of-mind questions),
Emotions category only (598 questions, 153 films). Model: Qwen2.5-Omni-7B, the text-producing part only, with no audio.
Confidence is the probability of each answer letter as the model's next token. Abstention is a fifth option,
"E. Cannot tell from the given information."

| Condition | Model input |
|---|---|
| Q_noE | question + options A–D |
| Q | question + options A–E |
| T | transcript + question + options |
| T_told | "A video of this scene exists, but it is not shown to you." + T (from experiment 06) |
| VT | T + 64 silent frames of the clip |
| VTmis | T + 64 silent frames of a clip from a different film |

From experiment 06 the options are shown in a random order per question (the same in every condition), and after the
answer the model gets two separate follow-up questions: a free-form explanation of the information it used, and a
four-option evidence question (nothing else / a transcript / a video / both). Exact texts are in the
[config](configs/2026-10-18_full_shuffled.toml).

## Experiments

| Date | Experiment | Notebook | Config | Results |
|---|---|---|---|---|
| 2026-09-28 | Pilot: T vs VT, options A–D | [04](notebooks/04_2026-09-28_pilot_run.ipynb) | [config](configs/2026-09-28_pilot.toml) | [outputs](outputs/2026-09-28_pilot/) |
| 2026-10-04 | Abstention (option E), question-only floor, mismatched video, one-sentence explanations | [05](notebooks/05_2026-10-04_abstain_mismatch_explain.ipynb) | [config](configs/2026-10-04_abstain_mismatch_explain.toml) | [outputs](outputs/2026-10-04_abstain_mismatch_explain/) |
| 2026-10-18 | As 05, all 598 questions, options in a random order (position-bias control), native-resolution frames, new condition T_told (told a video exists but is not shown), two follow-up branches (free-form explanation, evidence question), on a GPU | [06](notebooks/06_2026-10-18_full_shuffled.ipynb) | [config](configs/2026-10-18_full_shuffled.toml) | [outputs](outputs/2026-10-18_full_shuffled/) |

Each experiment notebook ends with its analysis and plots. Results are appended to `results.jsonl` one row per
(question, condition), so a run can be stopped and resumed, or extended with more questions.

## Results so far (experiment 06, all 598 questions)

- Abstention follows the evidence: question only 62%, transcript 47%, with the video 29%; a video from a different film
  raises it back to 42% (each step p < 0.001, paired).
- The video changes *whether* the model answers, not *how well*: the best of A–D is right about equally often with the
  transcript (55%), the video (56%) and the wrong video (53%).
- Told that a video exists but is not shown (T_told), it abstains as often as with the question only (62%), but mostly
  across the board rather than where the video matters.
- Self-report does not register the video: asked what it used, the model names a video in 6.5% of cases with its own
  video, and 9.2% with no video at all (question only, Q_noE). The explanations are not coded yet (keyword screens only).
- Slides: [slides/decks/2026-10-19_full_run.pptx](slides/decks/2026-10-19_full_run.pptx); all numbers in
  [notebook 06](notebooks/06_2026-10-18_full_shuffled.ipynb), including its "Additional tests" section.

## Files

```
notebooks/
  01_data_preprocessing.ipynb   build the question, transcript and video tables; check transcript-video sync
  02_model_check.ipynb          load the model, check letter scoring and video timing on one question
  03_select_questions.ipynb     keep Emotions questions, drop 1 broken clip, fix a random question order
  04_2026-09-28_pilot_run.ipynb pilot run + analysis
  05_2026-10-04_...ipynb        abstention / mismatch / explanations run + analysis
  06_2026-10-18_...ipynb        full run: shuffled options, two follow-up branches (GPU) + analysis
src/
  qwen_omni.py                  model loading, frame sampling, prompt building, letter scoring, text generation
  video_alignment.py            transcript-video sync check (used by notebook 01)
configs/                        one TOML per experiment: model revision, frames, prompt texts
outputs/<date>_<experiment>/    results.jsonl, figures/, other run outputs
files/                          slides and the MoMentS paper
slides/                         scripts that build the meeting slides (presentation tooling, not experiment code)
data-private/                   not in git (see below)
```

## Data

`data-private/` is git-ignored. Notebook 01 expects, under `data-private/raw/`:

- `moments_github/`: the public MoMentS repo (the commit is recorded in `SOURCE.txt`);
- `moments_questions_v4_test_keys.json`: **private** test answer keys from the MoMentS authors;
- `all_trimmed_trxs/` and `all_videos/`: transcripts and films from the MoMentS authors.

Notebook 01 writes the processed tables to `data-private/processed/`. Answer keys are kept in a separate table there
and are loaded only after a run, for analysis. Nothing under `outputs/` stores per-question answer keys (results,
explanations and saved notebook tables are key-free; only aggregate scores use the keys), so `outputs/` is in git.

## Setup

Python 3.12. `pip install -r requirements.txt`. The model (~18 GB RAM) runs on the GPU when there is one, otherwise on
CPU, where a question with video takes about 1–3 minutes, depending on the experiment. Experiment 06 (598 questions,
6 conditions, native-resolution frames) took 4.3 hours on one NVIDIA L40S (46 GB): about 1 s per text condition and
11 s per video condition.
