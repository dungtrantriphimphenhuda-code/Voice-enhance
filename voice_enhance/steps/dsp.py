import logging

import numpy as np

from ..config import DSPConfig

logger = logging.getLogger(__name__)


def process(audio: np.ndarray, sr: int, config: DSPConfig) -> np.ndarray:
    if not config.enabled:
        return audio

    try:
        import pedalboard
        from pedalboard import Pedalboard, HighpassFilter, Compressor, Limiter
    except ImportError:
        logger.warning("pedalboard not installed, falling back to no-op")
        return audio

    logger.info("Applying DSP chain (HPF -> DeEsser -> Comp -> Limiter)")

    board = Pedalboard(
        [
            HighpassFilter(cutoff_frequency_hz=config.highpass_cutoff),
            DeEsser(
                threshold_db=config.deesser_threshold,
                ratio=config.deesser_ratio,
            ),
            Compressor(
                threshold_db=config.comp_threshold,
                ratio=config.comp_ratio,
                attack_seconds=config.comp_attack,
                release_seconds=config.comp_release,
            ),
            Limiter(
                threshold_db=config.limiter_threshold,
                release_seconds=config.limiter_release,
            ),
        ]
    )

    if audio.ndim == 1:
        audio_2d = audio[np.newaxis, :]
    else:
        audio_2d = audio

    processed = board(audio_2d, sr)

    result = np.array(processed, dtype=np.float64)
    if result.ndim == 2 and result.shape[0] == 1:
        result = result[0]

    if config.makeup_gain != 0.0:
        gain_linear = 10 ** (config.makeup_gain / 20.0)
        result = result * gain_linear

    result = np.clip(result, -1.0, 1.0)

    return result


class DeEsser:
    def __init__(self, threshold_db: float = -20, ratio: float = 10):
        import pedalboard

        self._comp = pedalboard.Compressor(
            threshold_db=threshold_db,
            ratio=ratio,
            attack_seconds=0.001,
            release_seconds=0.050,
        )
        self._filter = pedalboard.HighpassFilter(cutoff_frequency_hz=6000)

    def __call__(self, audio, sample_rate):
        filtered = self._filter(audio, sample_rate)
        sidechain = self._comp(filtered, sample_rate)
        return sidechain
