"""PerceptionLM-8B: shared prompts and scoring from common; every second of the shared 64 frames (its context fits 32)."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from transformers import AutoProcessor, PerceptionLMForConditionalGeneration

import common
from common import LETTERS, LastPositionHead, build_prompt, score_options  # noqa: F401

MODEL_ID = "facebook/Perception-LM-8B"
END = "<|eot_id|>"


def load(revision):
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = PerceptionLMForConditionalGeneration.from_pretrained(MODEL_ID, revision=revision, dtype=torch.bfloat16)
    model.lm_head = LastPositionHead(model.lm_head)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model


def sample_frames(video_path, t_start, t_end, n_frames, max_pixels=None):
    frames, fps = common.sample_frames(video_path, t_start, t_end, n_frames, max_pixels)
    return frames[::2], fps / 2


def make_inputs(processor, system_text, user_text, frames=None, fps=None, followup=None):
    """As common.make_inputs; each frame is resized to 448x448 by the processor; the template already adds the start token."""
    content = [{"type": "text", "text": user_text}]
    if frames is not None:
        content = [{"type": "video"}] + content
    messages = [{"role": "user", "content": content}]
    if system_text is not None:
        messages = [{"role": "system", "content": system_text}] + messages
    if followup is not None:
        messages += [
            {"role": "assistant", "content": [{"type": "text", "text": followup[0]}]},
            {"role": "user", "content": [{"type": "text", "text": followup[1]}]},
        ]
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    if frames is None:
        return processor(text=prompt, add_special_tokens=False, return_tensors="pt"), prompt
    return processor(text=prompt, videos=[frames], add_special_tokens=False, return_tensors="pt"), prompt


@torch.inference_mode()
def generate_text(model, processor, inputs, max_new_tokens):
    end_id = processor.tokenizer.convert_tokens_to_ids(END)
    inputs = inputs.to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, eos_token_id=end_id, pad_token_id=end_id)
    new = out[0, inputs["input_ids"].shape[1]:]
    hit_limit = len(new) == max_new_tokens and new[-1].item() != end_id
    return {"text": processor.tokenizer.decode(new, skip_special_tokens=True).strip(),
            "n_tokens": len(new), "hit_limit": hit_limit}
