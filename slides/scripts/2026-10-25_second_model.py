"""Run from the repo root: python slides/scripts/2026-10-25_second_model.py"""
from deck import ROOT, new_deck, slide, table_slide, title_slide

OUT = ROOT / "slides/decks/2026-10-25_second_model.pptx"
FIG = "outputs/2026-10-25_compare_models/figures"


def add_slides(prs):
    slide(prs, "Second model: InternVL2.5-8B", [
        "The only non-Qwen open model evaluated in the MoMentS paper (InternLM2.5 language model, InternViT vision).",
        (1, "Release used: OpenGVLab/InternVL2_5-8B-MPO-hf (runs natively in transformers)."),
        "Same as Qwen: 598 questions, six conditions, prompts, option orders, 64 frames, both follow-up questions.",
        (1, "Each frame is one 448x448 image; letter probabilities sum to 1.0 in every condition."),
        "Explanations coded by the same two judges, same prompt (notebook 09).",
        (1, "Agreement: kappa 0.87 dialogue, 0.85 visual, 0.99 insufficient, 0.73 missing visual."),
        "Comparison in notebook 10.",
    ])

    table_slide(prs, "Both models, 598 questions", [
        "", "Model", "Q", "T", "T_told", "VT", "VTmis"], [
        ["Abstained", "Qwen", "61.7%", "47.5%", "61.9%", "29.4%", "41.6%"],
        ["", "InternVL", "58.7%", "42.0%", "53.8%", "13.7%", "15.7%"],
        ["Best A-D answer right", "Qwen", "45.3%", "54.7%", "55.2%", "56.2%", "52.5%"],
        ["", "InternVL", "43.0%", "51.2%", "52.7%", "56.4%", "49.0%"],
        ["Confidently wrong (>= 0.8)", "Qwen", "9.0%", "12.0%", "8.0%", "13.9%", "15.1%"],
        ["", "InternVL", "9.2%", "10.5%", "7.7%", "14.0%", "13.9%"],
    ], bullets=[
        "Q_noE (no \"Cannot tell\"): confidently wrong 16.6% Qwen, 15.2% InternVL.",
    ], body_height=450000, font_size=12)

    slide(prs, "Abstention: same pattern, except for the wrong video", [
        "Both abstain less with more evidence, more when told a video exists.",
        "Wrong video: Qwen 29% to 42% (p < 0.001), InternVL 14% to 16% (p = 0.22).",
    ], figure=f"{FIG}/abstention_by_model.png", body_height=800000)

    slide(prs, "InternVL: the wrong video hurts, unnoticed", [
        "Best A-D answer right: 56.4% with the right video, 49.0% with the wrong one (81 lost, 37 gained, p < 0.001).",
        (1, "Below the transcript alone (51.2%): the wrong video misleads it."),
        "Yet it abstains only 2 points more, and still says it used a video in 48%.",
        "Qwen: smaller loss (56.2% to 52.5%, p = 0.04), but abstains 12 points more.",
        "Neither model's explanations notice a wrong video (0 of 598 each, both judges).",
        (1, "The one InternVL explanation flagged (right video) disputes the question's premise."),
    ])

    slide(prs, "Self-report: a video, not its relevance", [
        "InternVL claims a video in 63% (right), 48% (wrong video), 14% (none).",
        "Qwen rarely claims one; both cite things seen with the wrong video.",
    ], figure=f"{FIG}/video_self_report_by_model.png", body_height=800000)

    slide(prs, "Told a video exists (T_told): replicates", [
        "Both abstain more: Qwen 47.5% to 61.9% (87 start, 1 stops), InternVL 42.0% to 53.8% (72 start, 1 stops).",
        "Mostly across the board: P(\"Cannot tell\") rises only a little more where the video mattered.",
        (1, "Qwen +0.14 vs +0.11; InternVL +0.10 vs +0.07 (both p < 0.001)."),
        "Explanations rarely name the missing video: Qwen 7.9%, InternVL 3.7%.",
        "InternVL: 5 T_told explanations refer to \"the audio\", though no audio is ever given.",
    ])

    slide(prs, "Takeaways", [
        "Replicates across model families:",
        (1, "abstention follows the evidence (C1); blanket caution when told evidence is missing;"),
        (1, "no explanation notices a video from the wrong film (C2)."),
        "Differs: InternVL's abstention ignores the wrong video, though its accuracy drops.",
        (1, "It reports using a video often, but about as often for the wrong one: self-report tracks"),
        (1, "whether a video is there, not whether it is relevant (C2)."),
        "Caveats: two 7-8B open models; explanation codes are LLM-judge labels (not hand-checked).",
        "Next: write the study section of the paper.",
    ])


if __name__ == "__main__":
    prs = new_deck()
    title_slide(prs, "AI Alignment paper: second model (InternVL2.5-8B)", "25.10.2026")
    add_slides(prs)
    prs.save(OUT)
    print("saved", OUT.relative_to(ROOT), "-", len(prs.slides), "slides")
