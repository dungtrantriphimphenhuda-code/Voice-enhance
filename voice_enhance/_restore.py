import os
import sys
import tempfile
import numpy as np
import soundfile as sf


def process(audio: np.ndarray, sr: int, cfg: dict) -> np.ndarray:
    try:
        from voicefixer import VoiceFixer
    except ImportError:
        print("! voicefixer chua cai -> bo qua restore", file=sys.stderr)
        return audio

    vf = VoiceFixer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, sr)
        out = tmp.name.replace(".wav", "_fixed.wav")
        try:
            vf.restore(input=tmp.name, output=out, mode=cfg.get("voicefixer_mode", "live"))
            if os.path.exists(out):
                result, _ = sf.read(out)
                os.unlink(out)
                return result
        finally:
            os.unlink(tmp.name)
    return audio
