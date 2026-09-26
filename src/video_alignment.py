"""Video alignment check: do the WhisperX word timings line up with speech in the local video file?

For one film: compare "is someone speaking?" (from transcript word times) with the loudness of the
film's own audio track, for time shifts of -15..+15 s. The shift with the highest correlation is the
film's offset (0 = aligned). The audio is used only for this check, never as model input.
Lives in a .py file because notebook 01 runs it in parallel worker processes.
"""
import av
import numpy as np

HZ = 10  # compare at 10 time steps per second
MAX_SHIFT_S = 15


def loudness(video_path):
    """Loudness of the audio track, one value per 1/HZ s, standardized to mean 0, sd 1."""
    rate = 8000
    with av.open(str(video_path)) as container:
        resampler = av.AudioResampler(format="s16", layout="mono", rate=rate)
        chunks = [out.to_ndarray().ravel()
                  for frame in container.decode(container.streams.audio[0])
                  for out in resampler.resample(frame)]
    x = np.concatenate(chunks).astype(np.float32)
    step = rate // HZ
    n = len(x) // step
    level = np.log(np.sqrt((x[: n * step].reshape(n, step) ** 2).mean(axis=1)) + 1)
    return (level - level.mean()) / (level.std() + 1e-9)


def film_shift(job):
    """job = (video_path, word_times [(start, end), ...], t_end). Returns (best shift in s, correlation at it)."""
    video_path, word_times, t_end = job
    audio = loudness(video_path)
    pad = MAX_SHIFT_S * HZ
    speaking = np.zeros(len(audio) + 2 * pad)
    for start, end in word_times:
        speaking[int(start * HZ): int(end * HZ) + 1] = 1
    t = np.arange(pad, min(len(audio), int(t_end * HZ)) - pad)  # time steps compared (keep clear of the edges)
    corr = {s / HZ: np.corrcoef(audio[t], speaking[t - s])[0, 1] for s in range(-pad, pad + 1)}
    best = max(corr, key=corr.get)
    return best, corr[best]
