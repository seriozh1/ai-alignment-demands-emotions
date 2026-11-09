# AI alignment demands emotions: empirical study

Empirical support for a position paper on the underdetermination of emotions and epistemic humility in AI.

**Question:** do a model's confidence and its willingness to abstain reflect whether it has the evidence humans need
to infer emotions? For example, when the answer depends on a face, does a transcript-only model abstain more than one
given the video?

**Setup:** [MoMentS](https://github.com/villacu/MoMentS) (short films with multiple-choice theory-of-mind questions),
Emotions category only (598 questions, 153 films). Models: seven open vision-language models (see [Runs](#runs)), with
no audio. Confidence is the probability of each answer letter as the model's next token. Abstention is a fifth option,
"E. Cannot tell from the given information."

| Condition | Model input |
|---|---|
| Q_noE | question + options A–D |
| Q | question + options A–E |
| T | transcript + question + options |
| T_told | "A video of this scene exists, but it is not shown to you." + T (full runs only) |
| VT | T + 64 silent frames of the clip |
| VTmis | T + 64 silent frames of a clip from a different film |

In the full runs the options are shown in a random order per question (the same in every condition and for every
model), and after the answer the model gets two separate follow-up questions: a free-form explanation of the
information it used, and a four-option evidence question (nothing else / a transcript / a video / both). Exact texts
are in [configs/full_run.toml](configs/full_run.toml).

## How to run

1. Data: `data_preprocessing.ipynb`, then `select_questions.ipynb`.
2. Run a model: `run_model.ipynb` with `MODEL` set to its name in `configs/models.toml` (GPU).
3. Code its explanations: `code_explanations.ipynb` with the same `MODEL` (OpenRouter).
4. Compare: `compare_models.ipynb`; it includes every model with results and codes in `outputs/<model>/`.

Configs: [full_run.toml](configs/full_run.toml) (frames, conditions, prompts; the same for every model),
[models.toml](configs/models.toml) (one entry per model: name, pinned revision, `src/` module) and
[judges.toml](configs/judges.toml) (judges, codes, prompt). To add a model: an entry in `models.toml` and a
`src/<module>.py` that provides the same functions as the others (`load`, `build_prompt`, `sample_frames`,
`make_inputs`, `score_options`, `generate_text`), taking from `src/common.py` whatever it does not change. A model that needs a different procedure (other conditions, audio, an older software
environment) gets its own notebook.

## Runs

One folder per model in `outputs/`, with `results.jsonl` (one row per question and condition), `explanations.csv`,
the judges' `judge_labels.jsonl`, `agreement.csv` and `codes_by_condition.csv`.

| Date | Model | Outputs |
|---|---|---|
| 2026-10-18 | Qwen2.5-Omni-7B (text-producing part only) | [outputs/qwen2.5-omni-7b](outputs/qwen2.5-omni-7b/) |
| 2026-10-25 | InternVL2.5-8B (`OpenGVLab/InternVL2_5-8B-MPO-hf`, the only non-Qwen open model in the MoMentS paper) | [outputs/internvl2.5-8b](outputs/internvl2.5-8b/) |
| 2026-10-25 | Qwen2.5-VL-7B-Instruct (MoMentS paper) | [outputs/qwen2.5-vl-7b](outputs/qwen2.5-vl-7b/) |
| 2026-10-26 | LLaVA-Video-7B-Qwen2 (MoMentS paper; community transformers conversion `Isotr0py/LLaVA-Video-7B-Qwen2-hf`) | [outputs/llava-video-7b](outputs/llava-video-7b/) |
| 2026-11-08 | Gemma 4 12B (`google/gemma-4-12B-it`, thinking off; a recent model from a non-Qwen family) | [outputs/gemma-4-12b](outputs/gemma-4-12b/) |
| 2026-11-08 | GLM-4.6V-Flash (`zai-org/GLM-4.6V-Flash`, 10B, thinking off; Zhipu GLM family, the largest GLM vision model that fits on one L40S; letters scored after its answer-box token, which it puts first) | [outputs/glm-4.6v-flash](outputs/glm-4.6v-flash/) |
| 2026-11-09 | PerceptionLM-8B (`facebook/Perception-LM-8B`; Meta, Llama 3.1 family; 32 of the shared 64 frames, its context limit) | [outputs/perception-lm-8b](outputs/perception-lm-8b/) |

All full runs: 598 questions, six conditions, the same prompts, frames and option orders. The Qwen2.5-Omni folder also
has `judge_labels_v1.jsonl`, an earlier coding run before `cites_dialogue` excluded speech repeated from the question.
The comparison of all models is in [outputs/compare_models/](outputs/compare_models/); which question gets which
wrong film (VTmis) is in [outputs/mismatch_pairs.csv](outputs/mismatch_pairs.csv), the same for every model.

Pilots, with Qwen2.5-Omni-7B (each notebook runs and analyses its own experiment):

| Date | Pilot | Notebook | Config | Results |
|---|---|---|---|---|
| 2026-09-28 | T vs VT, options A–D | [notebook](notebooks/pilot_2026-09-28_t_vs_vt.ipynb) | [config](configs/2026-09-28_pilot.toml) | [outputs](outputs/2026-09-28_pilot/) |
| 2026-10-04 | Abstention (option E), question-only floor, mismatched video, one-sentence explanations | [notebook](notebooks/pilot_2026-10-04_abstain_mismatch_explain.ipynb) | [config](configs/2026-10-04_abstain_mismatch_explain.toml) | [outputs](outputs/2026-10-04_abstain_mismatch_explain/) |

All numbers below are in [notebooks/compare_models.ipynb](notebooks/compare_models.ipynb).

## Results: Qwen2.5-Omni-7B

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
  [slides/decks/2026-10-19_summary.pptx](slides/decks/2026-10-19_summary.pptx).

## Results: InternVL2.5-8B

- Replicates: abstention falls with the transcript (59% to 42%) and the video (14%); told that a video exists, it
  abstains more (54%), again mostly across the board; no explanation notices a video from the wrong film.
- Differs: with the wrong film's video it abstains barely more (14% to 16%, p = 0.22; Qwen2.5-Omni 29% to 42%),
  although its best A–D answer is right less often (56.4% to 49.0%, p < 0.001; below the transcript alone, 51.2%).
- It says it used a video far more often than Qwen2.5-Omni (63% with its own video), but also 48% with the wrong one
  and 14% with none; its explanations cite things seen in 34%, 24% and 14%.
- Judges agree (kappa 0.73–0.99).

## Results: Qwen2.5-VL-7B

- Most cautious without a video (abstains 97% question only, 82% transcript, 87% T_told), 33% with the video; the
  wrong film's video raises it to 66% (211 start, 15 stop), the strongest reaction of the models.
- Its best A–D answer is right less often with the wrong video (59.7% to 51.0%, p < 0.001), as for the others.
- Says it used a video in 94% with its own video and still 63% with the wrong one.
- First model whose explanations sometimes say the frames do not show what the question is about (wrong video: 4 of 598
  by both judges, 13 by either); none say the clip is from another film. 34 wrong-video explanations mention "audio",
  which is never given.
- Judges agree (kappa 0.74–0.99; `notices_mismatch` 0.47, rare).

## Results: LLaVA-Video-7B

- Abstains least of the four models: 28% question only, 14% with the transcript; the right video changes neither
  abstention (14% to 15%) nor how often the best A–D answer is right (54% both).
- The wrong film's video raises abstention to 25% (74 start, 14 stop, p < 0.001) and lowers the best A–D answer
  (54% to 49%, p = 0.006).
- Told that a video exists (T_told), it abstains no more than with the transcript (11 start, 9 stop): the first model
  that does not react.
- Says it used a video in 41% with its own video, 32% with the wrong one, and 19% with none (Q_noE); explanations cite
  things seen in 21%, 17% and 6%; none notices the wrong video (the one mismatch flag by both judges is
  with the right video).
- Judges agree (kappa 0.71–0.98).

## Results: Gemma 4 12B

- Cautious without a video, like Qwen2.5-VL: abstains 96% question only, 81% with the transcript, 35% with the video;
  the wrong film's video raises it to 65% (193 start, 18 stop) and lowers the best A–D answer (57.2% to 51.0%,
  p < 0.001).
- Told that a video exists (T_told), it abstains more (81% to 86%), but not more where the video mattered.
- First model whose explanations often notice the wrong video: 24.6% (147 of 598, both judges) say the clip does not
  show the scene in the question. Still, 41% of wrong-video explanations cite things seen, and it says it used a video
  in 78%.
- Without any video (Q_noE), 22% of its explanations cite things seen (e.g. facial expressions).
- Without option E it often starts a sentence instead of a letter: in 44% of Q_noE questions less than half of the
  probability is on A–D.
- Judges agree (kappa 0.72–0.99).

## Results: GLM-4.6V-Flash

- Abstains 62% question only, 48% with the transcript, 32% with the video; the wrong film's video raises it to 61%
  (185 start, 10 stop) and lowers the best A–D answer from 64.7% (highest of the models) to 52.3%.
- Told that a video exists (T_told), it abstains a little more (48% to 52%), slightly more where the video mattered
  (+0.060 vs +0.038 P(E), p = 0.012).
- 9.2% of wrong-video explanations notice the mismatch; 23% still cite things seen.
- Its evidence-question answers follow the letter position (the option shown as C is picked 34–47% of the time), so
  "says it used a video" (66% even without one) is unreliable for GLM; its explanations are the better self-report.
- Judges agree (kappa 0.79–0.99).

## Results: PerceptionLM-8B

- Abstains least of all models without evidence (16% question only) and, unlike every other model, more with the
  transcript (31%; 126 start, 38 stop). The video lowers it to 17%, the wrong film's video raises it to 33% (120 start,
  26 stop) and lowers the best A–D answer from 57% to 47%.
- Told that a video exists (T_told), it hardly changes (31% to 32%; 23 start, 15 stop, p = 0.3).
- Cites things seen in 25% of explanations without any video (Q_noE), the most of all models, and in 45% with the wrong
  video; 1.0% notice the mismatch.
- Judges agree (kappa 0.70–0.96; the lowest is notices_mismatch, only about 10 positives).

## Files

```
notebooks/
  data_preprocessing.ipynb      build the question, transcript and video tables; check transcript-video sync
  select_questions.ipynb        keep Emotions questions, drop 1 broken clip, fix a random question order
  run_model.ipynb               run one model on all questions; GPU
  code_explanations.ipynb       code one model's explanations with two LLM judges; agreement, codes by condition
  compare_models.ipynb          all statistics, tables and figures for all models
  paper_figures.ipynb           paper tables and figures (into files/latex-paper/experiment/)
  pilot_2026-09-28_t_vs_vt.ipynb                    pilot run + analysis
  pilot_2026-10-04_abstain_mismatch_explain.ipynb   pilot: abstention / mismatch / explanations + analysis
src/
  common.py                     shared by every model: frame sampling, prompts, letter scoring, text generation
  qwen_omni.py                  Qwen2.5-Omni-7B: loading (the rest from common)
  internvl.py                   InternVL2.5-8B: loading, inputs, scoring
  qwen_vl.py                    Qwen2.5-VL-7B: loading, inputs
  llava_video.py                LLaVA-Video-7B: loading
  gemma4.py                     Gemma 4 12B: loading, inputs, text generation
  glm4v.py                      GLM-4.6V-Flash: loading, inputs, scoring, text generation
  perception_lm.py              PerceptionLM-8B: loading, 32 frames, inputs, text generation
  video_alignment.py            transcript-video sync check (used by data_preprocessing.ipynb)
configs/
  full_run.toml                 frames, conditions, prompts, option order: the same for every model
  models.toml                   one entry per model: name, pinned revision, module
  judges.toml                   judges, codes, prompt for coding the explanations
  2026-*_pilot*.toml, ...       the two pilots
outputs/
  <model>/                      results, explanations, judge labels, agreement, codes by condition
  compare_models/               comparison tables and figures
  mismatch_pairs.csv            the wrong film's clip for each question (VTmis), the same for every model
  2026-09-28_pilot/, 2026-10-04_.../   the two pilots
files/                          slides and the MoMentS paper
slides/                         helpers and finished decks for meeting slides (presentation tooling)
data-private/                   not in git (see below)
```

## Data

`data-private/` is git-ignored. `data_preprocessing.ipynb` expects, under `data-private/raw/`:

- `moments_github/`: the public MoMentS repo (the commit is recorded in `SOURCE.txt`);
- `moments_questions_v4_test_keys.json`: **private** test answer keys from the MoMentS authors;
- `all_trimmed_trxs/` and `all_videos/`: transcripts and films from the MoMentS authors.

`data_preprocessing.ipynb` writes the processed tables to `data-private/processed/`. Answer keys are kept in a separate
table there and are loaded only after a run, for analysis. Nothing under `outputs/` stores per-question answer keys
(results, explanations and saved notebook tables are key-free; only aggregate scores use the keys), so `outputs/` is
in git.

## Setup

Python 3.12. `pip install -r requirements.txt`. The models run on the GPU when there is one, otherwise on CPU, where a
question with video takes about 1–3 minutes. On one NVIDIA L40S (46 GB) a full run (598 questions, 6 conditions) takes
3.7–6.4 hours depending on the model (22–39 s per question). `code_explanations.ipynb` needs `OPENROUTER_API_KEY` in a
git-ignored `.env`; a full judge run costs about $2.
