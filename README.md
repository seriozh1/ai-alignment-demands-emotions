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
| 2026-10-19 | Coding of 06's free-form explanations: five yes/no codes, two LLM judges (Claude Haiku 5.5, GPT-6 Luna, via OpenRouter); `judge_labels_v1.jsonl` is the first run, before `cites_dialogue` excluded speech repeated from the question | [07](notebooks/07_2026-10-19_code_explanations.ipynb) | [config](configs/2026-10-19_code_explanations.toml) | [outputs](outputs/2026-10-19_code_explanations/) |
| 2026-10-25 | As 06 with a second model, InternVL2.5-8B (the only non-Qwen open model in the MoMentS paper) | [08](notebooks/08_2026-10-25_internvl_full.ipynb) | [config](configs/2026-10-25_internvl_full.toml) | [outputs](outputs/2026-10-25_internvl_full/) |
| 2026-10-25 | Coding of 08's explanations, as 07 (same judges and prompt) | [09](notebooks/09_2026-10-25_code_explanations_internvl.ipynb) | [config](configs/2026-10-25_code_explanations_internvl.toml) | [outputs](outputs/2026-10-25_code_explanations_internvl/) |
| 2026-10-25 | Qwen vs InternVL: behavior, evidence question, explanation codes (no model needed) | [10](notebooks/10_2026-10-25_compare_models.ipynb) | - | [outputs](outputs/2026-10-25_compare_models/) |
| 2026-10-25 | As 06 with a third model, Qwen2.5-VL-7B-Instruct (MoMentS paper) | [11](notebooks/11_2026-10-25_qwen25vl_full.ipynb) | [config](configs/2026-10-25_qwen25vl_full.toml) | [outputs](outputs/2026-10-25_qwen25vl_full/) |
| 2026-10-26 | Coding of 11's explanations, as 07 (same judges and prompt) | [12](notebooks/12_2026-10-26_code_explanations_qwen25vl.ipynb) | [config](configs/2026-10-26_code_explanations_qwen25vl.toml) | [outputs](outputs/2026-10-26_code_explanations_qwen25vl/) |
| 2026-10-26 | Qwen-Omni vs InternVL vs Qwen-VL, as 10 (no model needed) | [13](notebooks/13_2026-10-26_compare_three_models.ipynb) | - | [outputs](outputs/2026-10-26_compare_three_models/) |

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
  video, and 9.2% with no video at all (question only, Q_noE); it claims a transcript in 36% with none.
- The explanations (both judges agree; kappa 0.79–0.98): with a video from a different film the model cites things seen
  about as often as with the right one (15.2% vs 16.4%), and no explanation notices the mismatch; with no video at all,
  6.9% cite things seen; told that a video exists, 7.9% name the missing video.
- Slides: [slides/decks/2026-10-19_full_run.pptx](slides/decks/2026-10-19_full_run.pptx),
  [slides/decks/2026-10-25_final_coding.pptx](slides/decks/2026-10-25_final_coding.pptx),
  [slides/decks/2026-10-25_second_model.pptx](slides/decks/2026-10-25_second_model.pptx) and the summary
  [slides/decks/2026-10-19_summary.pptx](slides/decks/2026-10-19_summary.pptx); numbers in
  [notebook 06](notebooks/06_2026-10-18_full_shuffled.ipynb) (including its "Additional tests" section) and
  [notebook 07](notebooks/07_2026-10-19_code_explanations.ipynb).

## Second model (experiments 08–10, InternVL2.5-8B)

- Replicates: abstention falls with the transcript (59% to 42%) and the video (14%); told that a video exists, it
  abstains more (54%), again mostly across the board; no explanation notices a video from the wrong film.
- Differs: with the wrong film's video it abstains barely more (14% to 16%, p = 0.22; Qwen 29% to 42%), although its
  best A–D answer is right less often (56.4% to 49.0%, p < 0.001; below the transcript alone, 51.2%).
- It says it used a video far more often than Qwen (63% with its own video), but also 48% with the wrong one and 14%
  with none; its explanations cite things seen in 34%, 24% and 14%.
- Judges agree as for Qwen (kappa 0.73–0.99). Numbers in [notebook 10](notebooks/10_2026-10-25_compare_models.ipynb).

## Third model (experiments 11–13, Qwen2.5-VL-7B)

- Most cautious without a video (abstains 97% question only, 82% transcript, 87% T_told), 33% with the video; the
  wrong film's video raises it to 66% (211 start, 15 stop), the strongest reaction of the three models.
- Its best A–D answer is right less often with the wrong video (59.7% to 51.0%, p < 0.001), as for the other two.
- Says it used a video in 94% with its own video and still 63% with the wrong one.
- First model whose explanations sometimes say the frames do not show what the question is about (wrong video: 4 of 598
  by both judges, 13 by either); none say the clip is from another film. 34 wrong-video explanations mention "audio",
  which is never given.
- Judges agree (kappa 0.74–0.99; `notices_mismatch` 0.47, rare). Numbers in
  [notebook 13](notebooks/13_2026-10-26_compare_three_models.ipynb).

## Files

```
notebooks/
  01_data_preprocessing.ipynb   build the question, transcript and video tables; check transcript-video sync
  02_model_check.ipynb          load the model, check letter scoring and video timing on one question
  03_select_questions.ipynb     keep Emotions questions, drop 1 broken clip, fix a random question order
  04_2026-09-28_pilot_run.ipynb pilot run + analysis
  05_2026-10-04_...ipynb        abstention / mismatch / explanations run + analysis
  06_2026-10-18_...ipynb        full run: shuffled options, two follow-up branches (GPU) + analysis
  07_2026-10-19_...ipynb        explanation coding with two LLM judges + agreement and codes by condition
  08_2026-10-25_...ipynb        as 06 with InternVL2.5-8B
  09_2026-10-25_...ipynb        as 07 for 08's explanations
  10_2026-10-25_...ipynb        Qwen vs InternVL comparison (tables and figures)
  11_2026-10-25_...ipynb        as 06 with Qwen2.5-VL-7B
  12_2026-10-26_...ipynb        as 07 for 11's explanations
  13_2026-10-26_...ipynb        three-model comparison (tables and figures)
src/
  qwen_omni.py                  model loading, frame sampling, prompt building, letter scoring, text generation
  internvl.py                   the same for InternVL2.5-8B (same prompts and frames)
  qwen_vl.py                    the same for Qwen2.5-VL-7B
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
11 s per video condition. Notebook 07 needs `OPENROUTER_API_KEY` in a git-ignored `.env`; a full judge run costs
about $1.90.
