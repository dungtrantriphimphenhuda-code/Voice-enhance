"""Example: process a single audio file with custom settings."""

from voice_enhance.config import (
    PipelineConfig,
    DenoiseConfig,
    RestoreConfig,
    DSPConfig,
    NormalizeConfig,
)
from voice_enhance.pipeline import VoiceEnhancePipeline

config = PipelineConfig(
    sample_rate=48000,
    denoise=DenoiseConfig(enabled=True, engine="deepfilternet"),
    restore=RestoreConfig(enabled=True, engine="voicefixer", voicefixer_mode="live"),
    dsp=DSPConfig(
        enabled=True,
        highpass_cutoff=80.0,
        deesser_threshold=-20.0,
        comp_threshold=-18.0,
        comp_ratio=3.0,
        makeup_gain=2.0,
        limiter_threshold=-1.0,
    ),
    normalize=NormalizeConfig(enabled=True, target_lufs=-16.0),
    keep_intermediate=True,
)

pipeline = VoiceEnhancePipeline(config)
result = pipeline.process_file("input.wav", "output/enhanced.wav")
print(f"Enhanced audio saved to: {result}")
