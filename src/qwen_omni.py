"""Qwen2.5-Omni-7B, Thinker only and no audio: frames, prompts, letter scores, explanations."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")  # keeps reserved GPU memory from piling up
import torch

os.environ.setdefault("FORCE_QWENVL_VIDEO_READER", "decord")  # same frames as all runs so far
from qwen_omni_utils.v2_5.vision_process import fetch_video
from transformers import Qwen2_5OmniProcessor, Qwen2_5OmniThinkerForConditionalGeneration

MODEL_ID = "Qwen/Qwen2.5-Omni-7B"
LETTERS = ["A", "B", "C", "D"]
SYSTEM_PROMPT = "You are a helpful assistant."  # Qwen's default


def build_prompt(question, with_transcript=True, option_e=None, order=None):
    """order: original letters in display order, e.g. ["C", "E", "A", "D", "B"]; None = A-D, then E."""
    texts = {letter: question["option_" + letter].strip() for letter in LETTERS}
    if option_e is not None:
        texts["E"] = option_e
    order = order or list(texts)
    assert sorted(order) == sorted(texts), order
    options = [f"{shown}. {texts[original]}" for shown, original in zip("ABCDE", order)]
    text = f"Question: {question['question'].strip()}\n" + "\n".join(options) + "\n\nAnswer with the option's letter only."
    if with_transcript:
        transcript = question["transcript_focused"] or "(no dialogue)"
        text = f"Transcript of the dialogue in the clip:\n{transcript}\n\n" + text
    return text


class LastPositionHead(torch.nn.Module):
    """Output layer on the last position only: same scores, without GBs of unused scores for video prompts."""

    def __init__(self, head):
        super().__init__()
        self.head = head

    def forward(self, hidden_states):
        return self.head(hidden_states[:, -1:, :])


def load(revision):
    processor = Qwen2_5OmniProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(
        MODEL_ID, revision=revision, dtype=torch.bfloat16
    )
    model.lm_head = LastPositionHead(model.lm_head)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model


def sample_frames(video_path, t_start, t_end, n_frames, max_pixels=None):
    video = {"video": str(video_path), "video_start": t_start, "video_end": t_end, "nframes": n_frames}
    if max_pixels is not None:
        video["max_pixels"] = max_pixels
    return fetch_video(video, return_video_sample_fps=True)


def make_inputs(processor, system_text, user_text, frames=None, fps=None, followup=None):
    """followup=(assistant_text, user_text) adds the model's answer and a second user turn."""
    content = [{"type": "text", "text": user_text}]
    if frames is not None:
        content = [{"type": "video"}] + content
    messages = [{"role": "user", "content": content}]
    if system_text is not None:
        messages = [{"role": "system", "content": [{"type": "text", "text": system_text}]}] + messages
    if followup is not None:
        messages += [
            {"role": "assistant", "content": [{"type": "text", "text": followup[0]}]},
            {"role": "user", "content": [{"type": "text", "text": followup[1]}]},
        ]
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    if frames is None:
        return processor(text=prompt, return_tensors="pt"), prompt
    return processor(text=prompt, videos=[frames], fps=fps, cap_pixels_per_frame=True, return_tensors="pt"), prompt


@torch.inference_mode()
def score_options(model, processor, inputs, letters=LETTERS):
    letter_ids = [processor.tokenizer.convert_tokens_to_ids(letter) for letter in letters]
    inputs = inputs.to(model.device)
    logits = model(**inputs).logits[0, -1].float()
    logprobs = torch.log_softmax(logits, dim=-1)[letter_ids]
    return {
        "prob": torch.softmax(logprobs, dim=0).tolist(),  # renormalized over the letters
        "mass_on_letters": logprobs.exp().sum().item(),  # share of all next-token probability on the letters
        "logprob": logprobs.tolist(),
        "n_input_tokens": inputs["input_ids"].shape[1],
    }


@torch.inference_mode()
def generate_text(model, processor, inputs, max_new_tokens):
    end_id = processor.tokenizer.convert_tokens_to_ids("<|im_end|>")
    inputs = inputs.to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, eos_token_id=end_id, pad_token_id=end_id)
    new = out[0, inputs["input_ids"].shape[1]:]
    hit_limit = len(new) == max_new_tokens and new[-1].item() != end_id
    return {"text": processor.tokenizer.decode(new, skip_special_tokens=True).strip(),
            "n_tokens": len(new), "hit_limit": hit_limit}
