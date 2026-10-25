"""Qwen2.5-VL-7B-Instruct: same interface, prompts, frames and scoring as qwen_omni."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from qwen_omni import LETTERS, LastPositionHead, build_prompt, generate_text, sample_frames, score_options  # noqa: F401

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"


def load(revision):
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_ID, revision=revision, dtype=torch.bfloat16)
    model.lm_head = LastPositionHead(model.lm_head)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model


def make_inputs(processor, system_text, user_text, frames=None, fps=None, followup=None):
    """As qwen_omni.make_inputs; the frame rate goes in as video metadata (this processor ignores fps=)."""
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
    metadata = [{"total_num_frames": len(frames), "fps": fps}]
    return processor(text=prompt, videos=[frames], video_metadata=metadata, cap_pixels_per_frame=True,
                     return_tensors="pt"), prompt
