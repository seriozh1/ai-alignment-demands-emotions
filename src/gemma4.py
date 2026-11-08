"""Gemma 4 12B (instruction-tuned, thinking off): same interface, prompts, frames and scoring as qwen_omni."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from transformers import AutoModelForMultimodalLM, AutoProcessor

from qwen_omni import LETTERS, LastPositionHead, build_prompt, sample_frames, score_options  # noqa: F401

MODEL_ID = "google/gemma-4-12B-it"
END = "<turn|>"


def load(revision):
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = AutoModelForMultimodalLM.from_pretrained(MODEL_ID, revision=revision, dtype=torch.bfloat16)
    model.lm_head = LastPositionHead(model.lm_head)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model


def make_inputs(processor, system_text, user_text, frames=None, fps=None, followup=None):
    """As qwen_omni.make_inputs; our frames are used as given, their rate goes in as video metadata (for the timestamps)."""
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
    metadata = [{"total_num_frames": len(frames), "fps": fps, "frames_indices": list(range(len(frames)))}]
    return processor(text=prompt, videos=[frames], video_metadata=metadata, do_sample_frames=False,
                     return_tensors="pt"), prompt


@torch.inference_mode()
def generate_text(model, processor, inputs, max_new_tokens):
    end_id = processor.tokenizer.convert_tokens_to_ids(END)
    inputs = inputs.to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, eos_token_id=end_id,
                         pad_token_id=processor.tokenizer.pad_token_id)
    new = out[0, inputs["input_ids"].shape[1]:]
    hit_limit = len(new) == max_new_tokens and new[-1].item() != end_id
    return {"text": processor.tokenizer.decode(new, skip_special_tokens=True).strip(),
            "n_tokens": len(new), "hit_limit": hit_limit}
