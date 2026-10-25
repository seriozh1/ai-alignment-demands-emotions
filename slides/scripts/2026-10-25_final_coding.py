"""Run from the repo root: python slides/scripts/2026-10-25_final_coding.py"""
from deck import ROOT, new_deck, slide, table_slide, title_slide

OUT = ROOT / "slides/decks/2026-10-25_final_coding.pptx"


def add_slides(prs):
    slide(prs, "Explanation coding: one revision, final run", [
        "Revision after the first full run: speech that only repeats the question or options is not dialogue.",
        (1, "The same rule cites_visual already had; one new invented example in the prompt."),
        (1, "Before, dialogue copied from the question counted as citing a transcript."),
        "Both judges rerun on all 3,588 explanations (about $1.90, 1 h).",
        "Dialogue codes without a transcript: Q_noE 4.5% to 0.5%, Q 2.5% to 0.2%; other codes barely change.",
        "No hand-check for now: reliability = agreement between two judges from different providers.",
    ])

    table_slide(prs, "Final: the two judges agree closely", [
        "Code", "Agree", "Kappa", "Haiku yes", "Luna yes"], [
        ["cites_dialogue", "97.1%", "0.93", "998", "930"],
        ["cites_visual", "96.5%", "0.79", "337", "320"],
        ["says_insufficient", "99.3%", "0.98", "971", "966"],
        ["names_missing_visual", "99.1%", "0.83", "97", "113"],
        ["notices_mismatch", "99.9%", "-", "1", "3"],
    ], bullets=[
        "274 of 3,588 explanations (7.6%) have at least one disagreement.",
        "notices_mismatch: too rare for kappa; never flagged by both judges.",
    ], body_height=650000)

    table_slide(prs, "Final: what explanations claim (% both judges yes)", [
        "Condition", "It had", "Dialogue", "Visual", "Insufficient", "Missing visual", "Mismatch", "Judges differ"], [
        ["Q_noE", "nothing", "0.5", "6.9", "0.0", "0.0", "0.0", "3.3"],
        ["Q", "nothing", "0.2", "1.5", "51.8", "2.0", "0.0", "5.5"],
        ["T", "transcript", "46.7", "2.2", "29.1", "1.5", "0.0", "9.9"],
        ["T_told", "transcript", "63.2", "2.2", "47.3", "7.9", "0.0", "9.9"],
        ["VT", "both", "20.9", "16.4", "14.2", "2.0", "0.0", "9.0"],
        ["VTmis", "both, other film", "21.1", "15.2", "17.4", "1.3", "0.0", "8.2"],
    ], bullets=[
        "598 explanations per condition; notebook 07, codes_by_condition.csv.",
    ], body_height=400000, font_size=11)

    slide(prs, "Final result: the wrong video goes unnoticed (C2)", [
        "Wrong film's video: cites things seen about as often as with the right one (15.2% vs 16.4%).",
        "No explanation notices a mismatch (none flagged by both judges; one judge flags 4, none about the film).",
        "No video at all (Q_noE): 6.9% cite things seen.",
        (1, "\"... feeling disapproving and fearful based on his facial expression and body language.\""),
        "Claims audio, which the model never gets: 20 explanations without a transcript (keyword).",
        "Told a video exists (T_told): 47.3% say information is insufficient, only 7.9% name the video.",
    ])

    slide(prs, "Next steps", [
        "Second model from another family: InternVL2.5-8B (InternLM2.5 language model).",
        (1, "The only non-Qwen open model evaluated in the MoMentS paper (T 46.0, VT 46.6)."),
        (1, "Same conditions, prompts, frames and follow-ups (notebook 08); then the same judges."),
        "Write the study section of the paper with these results.",
    ])


if __name__ == "__main__":
    prs = new_deck()
    title_slide(prs, "AI Alignment paper: final explanation coding", "25.10.2026")
    add_slides(prs)
    prs.save(OUT)
    print("saved", OUT.relative_to(ROOT), "-", len(prs.slides), "slides")
