import numpy as np


def process(audio: np.ndarray, sr: int, cfg: dict) -> np.ndarray:
    try:
        import pedalboard
        from pedalboard import Pedalboard, HighpassFilter, Compressor, Limiter
    except ImportError:
        return audio

    x = audio[np.newaxis, :] if audio.ndim == 1 else audio
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=cfg.get("hpf_cutoff", 80)),
        _DeEsser(cfg.get("deesser_threshold", -20), cfg.get("deesser_ratio", 10)),
        Compressor(
            threshold_db=cfg.get("comp_threshold", -18),
            ratio=cfg.get("comp_ratio", 3),
            attack_seconds=0.001, release_seconds=0.05,
        ),
        Limiter(threshold_db=cfg.get("limiter_threshold", -1), release_seconds=0.1),
    ])

    out = np.array(board(x, sr), dtype=np.float64)
    if out.ndim == 2 and out.shape[0] == 1:
        out = out[0]
    gain = 10 ** (cfg.get("makeup_gain", 2) / 20)
    return np.clip(out * gain, -1.0, 1.0)


class _DeEsser:
    def __init__(self, threshold, ratio):
        import pedalboard
        self._comp = pedalboard.Compressor(threshold_db=threshold, ratio=ratio, attack_seconds=0.001, release_seconds=0.05)
        self._filter = pedalboard.HighpassFilter(cutoff_frequency_hz=6000)

    def __call__(self, audio, sr):
        return self._comp(self._filter(audio, sr), sr)
