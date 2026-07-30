import logging
from pathlib import Path

import numpy as np
import soundfile as sf

from ..config import DenoiseConfig

logger = logging.getLogger(__name__)


def apply_deepfilternet(
    audio: np.ndarray,
    sr: int,
    config: DenoiseConfig,
) -> np.ndarray:
    try:
        import deepfilternet
        from deepfilternet import DFTParams
    except ImportError:
        logger.warning("deepfilternet not installed, falling back to no-op")
        return audio

    if audio.ndim == 1:
        audio = audio[None, :]

    df_config = DFTParams()
    df_config.model_name = config.deepfilternet_model
    df_config.post_filter = config.post_filter

    df = deepfilternet.DFT(df_config)
    processed = df(audio, sr)

    if processed.ndim == 2 and processed.shape[0] == 1:
        processed = processed[0]

    return processed


def apply_resemble_enhance(
    audio: np.ndarray,
    sr: int,
    config: DenoiseConfig,
) -> np.ndarray:
    try:
        import torch
        import torchaudio
        from resemble_enhance.enhancer import enhance
    except ImportError:
        logger.warning("resemble-enhance not installed, falling back to no-op")
        return audio

    device = "cuda" if torch.cuda.is_available() else "cpu"
    audio_t = torch.from_numpy(audio).float()
    if audio_t.ndim == 1:
        audio_t = audio_t.unsqueeze(0)

    dwav, d_sr = enhance(
        audio_t,
        sr,
        device=device,
        nfe=64,
        solver="midpoint",
        denoiser=True,
    )

    result = dwav.cpu().numpy()
    if result.ndim == 2 and result.shape[0] == 1:
        result = result[0]

    return result


def process(audio: np.ndarray, sr: int, config: DenoiseConfig) -> np.ndarray:
    if not config.enabled:
        return audio

    logger.info("Denoising with engine: %s", config.engine)

    if config.engine == "deepfilternet":
        return apply_deepfilternet(audio, sr, config)
    elif config.engine == "resemble":
        return apply_resemble_enhance(audio, sr, config)
    else:
        raise ValueError(f"Unknown denoise engine: {config.engine}")
