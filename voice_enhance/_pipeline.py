from pathlib import Path
import numpy as np
import soundfile as sf
from . import _denoise, _restore, _dsp, _normalize


DEFAULTS = {
    "sr": 48000,
    "denoise": True,
    "denoise_engine": "deepfilternet",
    "restore": True,
    "restore_engine": "voicefixer",
    "dsp": True,
    "hpf_cutoff": 80.0,
    "deesser_threshold": -20.0,
    "comp_threshold": -18.0,
    "comp_ratio": 3.0,
    "makeup_gain": 2.0,
    "limiter_threshold": -1.0,
    "normalize": True,
    "target_lufs": -16.0,
    "true_peak": -1.0,
    "output_dir": "output",
}


def run(input_path: str, output_path: str | None, overrides: dict) -> str:
    cfg = {**DEFAULTS, **overrides}
    src, dst = Path(input_path), Path(output_path or "")
    if not output_path:
        dst = Path(cfg["output_dir"]) / f"{src.stem}_enhanced.wav"
    dst.parent.mkdir(parents=True, exist_ok=True)

    audio, sr = sf.read(str(src))
    if audio.dtype not in (np.float32, np.float64):
        audio = audio.astype(np.float32)
    if sr != cfg["sr"]:
        audio = _resample(audio, sr, cfg["sr"])
        sr = cfg["sr"]

    if cfg["denoise"]:
        audio = _denoise.process(audio, sr, cfg)
    if cfg["restore"]:
        audio = _restore.process(audio, sr, cfg)
    if cfg["dsp"]:
        audio = _dsp.process(audio, sr, cfg)
    if cfg["normalize"]:
        audio = _normalize.process(audio, sr, cfg)

    sf.write(str(dst), audio, sr)
    return str(dst)


def _resample(audio, orig_sr, target_sr):
    try:
        import resampy
        return resampy.resample(audio, orig_sr, target_sr, axis=-1)
    except ImportError:
        ratio = target_sr / orig_sr
        n = int(len(audio) * ratio)
        return np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio)
