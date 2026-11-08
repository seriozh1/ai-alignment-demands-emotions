"""Qwen2.5-Omni-7B, Thinker only and no audio; the shared parts are in common."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from transformers import Qwen2_5OmniProcessor, Qwen2_5OmniThinkerForConditionalGeneration

from common import LETTERS, LastPositionHead, build_prompt, generate_text, make_inputs, sample_frames, score_options  # noqa: F401

MODEL_ID = "Qwen/Qwen2.5-Omni-7B"
SYSTEM_PROMPT = "You are a helpful assistant."  # Qwen's default


def load(revision):
    processor = Qwen2_5OmniProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(
        MODEL_ID, revision=revision, dtype=torch.bfloat16
    )
    model.lm_head = LastPositionHead(model.lm_head)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model
