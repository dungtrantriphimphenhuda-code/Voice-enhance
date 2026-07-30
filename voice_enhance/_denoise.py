import numpy as np


def process(audio: np.ndarray, sr: int, cfg: dict) -> np.ndarray:
    engine = cfg.get("denoise_engine", "deepfilternet")
    if engine == "deepfilternet":
        return _deepfilternet(audio, sr)
    elif engine == "resemble":
        return _resemble(audio, sr)
    return audio


def _deepfilternet(audio, sr):
    try:
        import deepfilternet
        from deepfilternet import DFTParams
    except ImportError:
        return audio

    x = audio[None, :] if audio.ndim == 1 else audio
    df = deepfilternet.DFT(DFTParams())
    out = df(x, sr)
    return out[0] if out.ndim == 2 and out.shape[0] == 1 else out


def _resemble(audio, sr):
    try:
        import torch
        from resemble_enhance.enhancer import enhance
    except ImportError:
        return audio

    device = "cuda" if torch.cuda.is_available() else "cpu"
    t = torch.from_numpy(audio).float().unsqueeze(0)
    dwav, _ = enhance(t, sr, device=device, nfe=64, solver="midpoint", denoiser=True)
    out = dwav.cpu().numpy()
    return out[0] if out.ndim == 2 and out.shape[0] == 1 else out
