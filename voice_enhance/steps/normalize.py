import logging

import numpy as np

from ..config import NormalizeConfig

logger = logging.getLogger(__name__)


def process(audio: np.ndarray, sr: int, config: NormalizeConfig) -> np.ndarray:
    if not config.enabled:
        return audio

    try:
        import pyloudnorm as pyln
    except ImportError:
        logger.warning("pyloudnorm not installed, falling back to peak normalize")
        peak = np.max(np.abs(audio))
        if peak > 0:
            target = 10 ** (config.true_peak_limit / 20.0)
            audio = audio * (target / peak)
        return audio

    logger.info(
        "Normalizing to %.1f LUFS (true peak: %.1f dBTP)",
        config.target_lufs,
        config.true_peak_limit,
    )

    if audio.ndim == 1:
        audio = audio.reshape(1, -1)

    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(audio.T)

    if np.isnan(loudness) or loudness == -float("inf"):
        logger.warning("Could not measure loudness, skipping LUFS normalization")
        return audio[0] if audio.shape[0] == 1 else audio

    gain_db = config.target_lufs - loudness
    gain_linear = 10 ** (gain_db / 20.0)
    audio = audio * gain_linear

    true_peak = np.max(np.abs(audio))
    if true_peak > 0.99:
        limit = 10 ** (config.true_peak_limit / 20.0)
        audio = audio * (limit / true_peak)

    if audio.shape[0] == 1:
        audio = audio[0]

    return audio
