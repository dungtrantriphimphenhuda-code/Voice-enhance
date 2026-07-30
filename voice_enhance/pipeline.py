import logging
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from .config import PipelineConfig
from .steps import denoise, restore, dsp, normalize

logger = logging.getLogger(__name__)


class VoiceEnhancePipeline:
    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig()

    def process_file(self, input_path: str, output_path: str | None = None) -> str:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input not found: {input_path}")

        if output_path is None:
            stem = input_path.stem
            output_path = Path(self.config.output_dir) / f"{stem}_enhanced.wav"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Loading: %s", input_path)
        audio, sr = sf.read(str(input_path))
        if audio.dtype != np.float64 and audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        if sr != self.config.sample_rate:
            logger.info("Resampling %d -> %d", sr, self.config.sample_rate)
            audio = self._resample(audio, sr, self.config.sample_rate)
            sr = self.config.sample_rate

        chain = [
            ("1.Denoise", denoise.process),
            ("2.Restore", restore.process),
            ("3.DSP", dsp.process),
            ("4.Normalize", normalize.process),
        ]

        current = audio
        intermediates = {}

        for stage_name, stage_fn in chain:
            cfg = getattr(self.config, stage_name.split(".")[-1].lower())
            t0 = time.perf_counter()
            current = stage_fn(current, sr, cfg)
            elapsed = time.perf_counter() - t0
            logger.info("  %s done in %.2fs", stage_name, elapsed)

            if self.config.keep_intermediate:
                inter_path = output_path.with_stem(
                    f"{output_path.stem}_{stage_name.split('.')[1].lower()}"
                )
                sf.write(str(inter_path), current, sr)
                intermediates[stage_name] = str(inter_path)

        sf.write(str(output_path), current, sr)
        logger.info("Saved: %s", output_path)

        if intermediates:
            logger.info("Intermediate files:")
            for name, path in intermediates.items():
                logger.info("  %s -> %s", name, path)

        return str(output_path)

    @staticmethod
    def _resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        try:
            import resampy
            return resampy.resample(audio, orig_sr, target_sr, axis=-1)
        except ImportError:
            try:
                import librosa
                return librosa.resample(y=audio, orig_sr=orig_sr, target_sr=target_sr, axis=-1)
            except ImportError:
                logger.warning("No resampler available, using naive method")
                ratio = target_sr / orig_sr
                n_samples = int(len(audio) * ratio)
                return np.interp(
                    np.linspace(0, len(audio) - 1, n_samples),
                    np.arange(len(audio)),
                    audio,
                )
