"""Run from the repo root: python slides/scripts/2026-10-19_summary.py"""
from deck import ROOT, new_deck, slide, table_slide, title_slide

OUT = ROOT / "slides/decks/2026-10-19_summary.pptx"


def add_slides(prs):
    slide(prs, "The study", [
        "An illustration of epistemic humility, not a theory-of-mind test.",
        (1, "C1: models are miscalibrated in emotion attribution."),
        (1, "C2: models may not register that the evidence they need is missing."),
        "Qwen2.5-Omni-7B, 598 MoMentS emotion questions, six conditions:",
        (1, "question only (with and without \"Cannot tell\"), + transcript, + \"a video exists\","),
        (1, "+ 64 silent frames of the clip, + frames from another film."),
        "After each answer: a one-sentence explanation and \"what did you base it on?\".",
        "Explanations coded by two LLM judges (Claude Haiku 5.5, GPT-6 Luna).",
    ])

    table_slide(prs, "Key results (598 questions)", [
        "", "Q", "T", "T_told", "VT", "VTmis"], [
        ["Abstained", "61.7%", "47.5%", "61.9%", "29.4%", "41.6%"],
        ["Best A-D answer right", "45.3%", "54.7%", "55.2%", "56.2%", "52.5%"],
        ["Confidently wrong (>= 0.8)", "9.0%", "12.0%", "8.0%", "13.9%", "15.1%"],
    ], bullets=[
        "Q: question only. T: + transcript. T_told: + \"a video exists\".",
        "VT: + video. VTmis: + another film's video.",
        "Without \"Cannot tell\" (Q_noE): 16.6% confidently wrong, the most.",
    ], body_height=1100000, font_size=14)

    slide(prs, "Behavior tracks evidence; confidence does not (C1)", [
        "Abstention falls with each piece of evidence (62% to 47% to 29%) and rises again with the wrong film's video (42%).",
        "But the video changes whether the model answers, not how well.",
        (1, "Best A-D answer right: 54.7% (T), 56.2% (VT), 52.5% (VTmis)."),
        (1, "The extra answers are about half right: 69 abstentions become right, 58 wrong."),
        "Confidently wrong is highest with a video, most with the wrong film's (15.1%).",
        "Told a video is missing (T_told): abstention back to 61.9%, but nearly across the board.",
        (1, "P(\"Cannot tell\") +0.14 where the video mattered, +0.11 where it did not."),
    ])

    slide(prs, "Self-report does not track the evidence (C2)", [
        "Rarely says it used the video: 6.5% when it had one, though its behavior depends on it.",
        "Claims evidence it never had:",
        (1, "a transcript in 36% with none; things seen in 6.9% of explanations with no video;"),
        (1, "\"the audio\" in 20 explanations, though it never gets audio (keyword search)."),
        "The wrong video goes unnoticed: cites things seen about as often as with the right one (15.2% vs 16.4%).",
        (1, "No explanation notices a mismatch (none flagged by both judges)."),
        "Told a video exists, only 7.9% of its explanations name the missing video.",
    ])

    slide(prs, "Takeaway and caveats", [
        "Epistemic humility needs both: behavior that tracks the evidence, and an accurate account of what evidence was there.",
        "Qwen partly has the first and largely lacks the second.",
        "So aligned emotion attribution needs models that know what evidence a judgement needs, not only higher accuracy.",
        "Caveats:",
        (1, "One model, silent frames (no audio); explanations come after the answer (self-report)."),
        (1, "Explanation codes are LLM-judge labels (two judges, kappa 0.79-0.98), not hand-checked."),
        (1, "MoMentS tags are optional, so subgroup results are exploratory."),
    ])


if __name__ == "__main__":
    prs = new_deck()
    title_slide(prs, "AI Alignment paper: summary of results", "19.10.2026")
    add_slides(prs)
    prs.save(OUT)
    print("saved", OUT.relative_to(ROOT), "-", len(prs.slides), "slides")
