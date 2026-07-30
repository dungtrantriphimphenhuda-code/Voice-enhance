import numpy as np
import soundfile as sf
import tempfile
import os

from voice_enhance.pipeline import VoiceEnhancePipeline
from voice_enhance.config import PipelineConfig, DenoiseConfig, RestoreConfig, DSPConfig, NormalizeConfig


def _generate_test_audio(sr=48000, duration=2.0):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)
    noise = 0.05 * np.random.randn(len(tone))
    return (tone + noise).astype(np.float32)


def test_pipeline_runs_end_to_end():
    audio = _generate_test_audio()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, 48000)
        input_path = f.name

    output_path = input_path.replace(".wav", "_out.wav")
    try:
        config = PipelineConfig(
            sample_rate=48000,
        )
        pipeline = VoiceEnhancePipeline(config)
        result = pipeline.process_file(input_path, output_path)
        assert os.path.exists(result)
        data, sr = sf.read(result)
        assert sr == 48000
        assert len(data) > 0
        assert not np.any(np.isnan(data))
        assert np.all(np.abs(data) <= 1.0)
    finally:
        for p in [input_path, output_path]:
            if os.path.exists(p):
                os.unlink(p)


def test_pipeline_skips_disabled_stages():
    audio = _generate_test_audio()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, 48000)
        input_path = f.name

    output_path = input_path.replace(".wav", "_out.wav")
    try:
        config = PipelineConfig(
            sample_rate=48000,
            denoise=DenoiseConfig(enabled=False),
            restore=RestoreConfig(enabled=False),
            dsp=DSPConfig(enabled=False),
            normalize=NormalizeConfig(enabled=False),
        )
        pipeline = VoiceEnhancePipeline(config)
        result = pipeline.process_file(input_path, output_path)
        assert os.path.exists(result)
        data_orig, _ = sf.read(input_path)
        data_out, _ = sf.read(result)
        assert np.allclose(data_orig, data_out, atol=1e-6)
    finally:
        for p in [input_path, output_path]:
            if os.path.exists(p):
                os.unlink(p)
