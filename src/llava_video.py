"""LLaVA-Video-7B-Qwen2 (community transformers conversion): shared prompts, frames and scoring from common."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from transformers import AutoProcessor, LlavaOnevisionForConditionalGeneration

from common import LETTERS, LastPositionHead, build_prompt, generate_text, make_inputs, sample_frames, score_options  # noqa: F401

MODEL_ID = "Isotr0py/LLaVA-Video-7B-Qwen2-hf"


def load(revision):
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = LlavaOnevisionForConditionalGeneration.from_pretrained(MODEL_ID, revision=revision, dtype=torch.bfloat16)
    model.lm_head = LastPositionHead(model.lm_head)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model
