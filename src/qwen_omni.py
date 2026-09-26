"""Qwen2.5-Omni-7B helpers: load the model, read video frames, build the prompt, score answers A-D.

Only the Thinker (the text-producing part) is loaded. Audio is never given to the model.
"""
import torch
from qwen_omni_utils.v2_5.vision_process import fetch_video  # Qwen's official video reader (uses decord)
from transformers import Qwen2_5OmniProcessor, Qwen2_5OmniThinkerForConditionalGeneration

MODEL_ID = "Qwen/Qwen2.5-Omni-7B"
LETTERS = ["A", "B", "C", "D"]
SYSTEM_PROMPT = "You are a helpful assistant."  # Qwen's default system prompt


def build_prompt(question):
    """User text for one question (a row of questions.parquet). Identical in T and VT; VT only adds the video."""
    transcript = question["transcript_focused"] or "(no dialogue)"
    options = "\n".join(f"{letter}. {question['option_' + letter].strip()}" for letter in LETTERS)
    return (
        f"Transcript of the dialogue in the clip:\n{transcript}\n\n"
        f"Question: {question['question'].strip()}\n{options}\n\n"
        "Answer with the option's letter only."
    )


def load(revision):
    processor = Qwen2_5OmniProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(
        MODEL_ID, revision=revision, dtype=torch.bfloat16
    )
    model.eval()
    return processor, model


def sample_frames(video_path, t_start, t_end, n_frames, max_pixels=None):
    """n_frames evenly spaced frames between t_start and t_end (seconds), read and resized by Qwen's own code.

    Returns (frames [T, 3, H, W], sampling fps). max_pixels=None uses Qwen's default frame size.
    """
    video = {"video": str(video_path), "video_start": t_start, "video_end": t_end, "nframes": n_frames}
    if max_pixels is not None:
        video["max_pixels"] = max_pixels
    return fetch_video(video, return_video_sample_fps=True)


def make_inputs(processor, system_text, user_text, frames=None, fps=None):
    """Build the chat prompt and turn it into model inputs.

    frames=None gives the T condition (text only); passing frames (and fps) from sample_frames gives VT.
    """
    content = [{"type": "text", "text": user_text}]
    if frames is not None:
        content = [{"type": "video"}] + content
    messages = [
        {"role": "system", "content": [{"type": "text", "text": system_text}]},
        {"role": "user", "content": content},
    ]
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    if frames is None:
        return processor(text=prompt, return_tensors="pt"), prompt
    return processor(text=prompt, videos=[frames], fps=fps, return_tensors="pt"), prompt


@torch.inference_mode()
def score_options(model, processor, inputs):
    """Probability the model gives to each answer letter as its next token."""
    letter_ids = [processor.tokenizer.convert_tokens_to_ids(letter) for letter in LETTERS]
    logits = model(**inputs).logits[0, -1].float()  # scores for the next token after the prompt
    logprobs = torch.log_softmax(logits, dim=-1)[letter_ids]
    return {
        "prob": torch.softmax(logprobs, dim=0).tolist(),  # renormalized over A-D, sums to 1
        "mass_on_letters": logprobs.exp().sum().item(),  # share of ALL next-token probability that went to A-D
        "logprob": logprobs.tolist(),
        "n_input_tokens": inputs["input_ids"].shape[1],
    }
