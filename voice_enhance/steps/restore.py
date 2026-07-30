import logging
import numpy as np

from ..config import RestoreConfig

logger = logging.getLogger(__name__)


def apply_voicefixer(audio: np.ndarray, sr: int, config: RestoreConfig) -> np.ndarray:
    try:
        from voicefixer import VoiceFixer
    except ImportError:
        logger.warning("voicefixer not installed, falling back to no-op")
        return audio

    import tempfile
    import os
    import soundfile as sf

    vf = VoiceFixer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_in:
        sf.write(tmp_in.name, audio, sr)
        tmp_out = tmp_in.name.replace(".wav", "_fixed.wav")
        try:
            vf.restore(
                input=tmp_in.name,
                output=tmp_out,
                mode=config.voicefixer_mode,
            )
            if os.path.exists(tmp_out):
                result, _ = sf.read(tmp_out)
                os.unlink(tmp_out)
                return result
        finally:
            os.unlink(tmp_in.name)

    return audio


def process(audio: np.ndarray, sr: int, config: RestoreConfig) -> np.ndarray:
    if not config.enabled:
        return audio

    logger.info("Restoring with engine: %s", config.engine)

    if config.engine == "voicefixer":
        return apply_voicefixer(audio, sr, config)
    else:
        raise ValueError(f"Unknown restore engine: {config.engine}")
