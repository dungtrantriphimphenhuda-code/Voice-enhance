import numpy as np


def process(audio: np.ndarray, sr: int, cfg: dict) -> np.ndarray:
    target = cfg.get("target_lufs", -16)
    peak_limit = cfg.get("true_peak", -1)

    try:
        import pyloudnorm as pyln
    except ImportError:
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio * (10 ** (peak_limit / 20) / peak)
        return audio

    x = audio.reshape(1, -1) if audio.ndim == 1 else audio
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(x.T)
    if np.isnan(loudness) or loudness == -float("inf"):
        return audio[0] if audio.shape[0] == 1 else audio

    x = x * (10 ** ((target - loudness) / 20))
    peak = np.max(np.abs(x))
    if peak > 0.99:
        x = x * (10 ** (peak_limit / 20) / peak)
    return x[0] if x.shape[0] == 1 else x
