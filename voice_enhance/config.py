from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DenoiseConfig:
    enabled: bool = True
    engine: str = "deepfilternet"
    deepfilternet_model: str = "DeepFilterNet2"
    post_filter: bool = True


@dataclass
class RestoreConfig:
    enabled: bool = True
    engine: str = "voicefixer"
    voicefixer_mode: str = "live"
    sr_ratio: float = 1.0


@dataclass
class DSPConfig:
    enabled: bool = True
    highpass_cutoff: float = 80.0
    deesser_threshold: float = -20.0
    deesser_ratio: float = 10.0
    comp_threshold: float = -18.0
    comp_ratio: float = 3.0
    comp_attack: float = 0.001
    comp_release: float = 0.050
    makeup_gain: float = 2.0
    limiter_threshold: float = -1.0
    limiter_release: float = 0.100


@dataclass
class NormalizeConfig:
    enabled: bool = True
    target_lufs: float = -16.0
    true_peak_limit: float = -1.0


@dataclass
class PipelineConfig:
    sample_rate: int = 48000
    denoise: DenoiseConfig = field(default_factory=DenoiseConfig)
    restore: RestoreConfig = field(default_factory=RestoreConfig)
    dsp: DSPConfig = field(default_factory=DSPConfig)
    normalize: NormalizeConfig = field(default_factory=NormalizeConfig)
    output_dir: str = "output"
    keep_intermediate: bool = False
