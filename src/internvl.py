"""InternVL2.5-8B (MPO, native transformers): same interface as qwen_omni, same prompts and frames."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch
from transformers import AutoProcessor, InternVLForConditionalGeneration

from qwen_omni import LETTERS, build_prompt, sample_frames  # noqa: F401

MODEL_ID = "OpenGVLab/InternVL2_5-8B-MPO-hf"
END = "<|im_end|>"


def load(revision):
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=revision)
    model = InternVLForConditionalGeneration.from_pretrained(MODEL_ID, revision=revision, dtype=torch.bfloat16)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    return processor, model


def make_inputs(processor, system_text, user_text, frames=None, fps=None, followup=None):
    """Frames go in as one 448x448 image each, "Frame1: <image>" ..., before the text, as in InternVL's own video chat."""
    if frames is not None:
        user_text = "".join(f"Frame{i + 1}: {processor.image_token}\n" for i in range(len(frames))) + user_text
    messages = [{"role": "user", "content": user_text}]
    if system_text is not None:
        messages = [{"role": "system", "content": system_text}] + messages
    if followup is not None:
        messages += [{"role": "assistant", "content": followup[0]}, {"role": "user", "content": followup[1]}]
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    if frames is None:
        return processor(text=prompt, return_tensors="pt"), prompt
    return processor(text=prompt, images=list(frames), crop_to_patches=False, return_tensors="pt"), prompt


def letter_ids(tokenizer, letter):
    """Both spellings of a letter: "A" (as after "assistant\\n") and "▁A"."""
    return [tokenizer.convert_tokens_to_ids(t) for t in (letter, "▁" + letter)]


@torch.inference_mode()
def score_options(model, processor, inputs, letters=LETTERS):
    inputs = inputs.to(model.device)
    logits = model(**inputs, logits_to_keep=1).logits[0, -1].float()
    all_logprobs = torch.log_softmax(logits, dim=-1)
    logprobs = torch.stack([all_logprobs[letter_ids(processor.tokenizer, letter)].logsumexp(0) for letter in letters])
    return {
        "prob": torch.softmax(logprobs, dim=0).tolist(),
        "mass_on_letters": logprobs.exp().sum().item(),
        "logprob": logprobs.tolist(),
        "n_input_tokens": inputs["input_ids"].shape[1],
    }


@torch.inference_mode()
def generate_text(model, processor, inputs, max_new_tokens):
    end_id = processor.tokenizer.convert_tokens_to_ids(END)
    inputs = inputs.to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, eos_token_id=end_id, pad_token_id=end_id)
    new = out[0, inputs["input_ids"].shape[1]:]
    hit_limit = len(new) == max_new_tokens and new[-1].item() != end_id
    return {"text": processor.tokenizer.decode(new, skip_special_tokens=True).strip(),
            "n_tokens": len(new), "hit_limit": hit_limit}
