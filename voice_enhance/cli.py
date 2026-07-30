import argparse
import logging
import sys
from pathlib import Path

from .config import (
    PipelineConfig,
    DenoiseConfig,
    RestoreConfig,
    DSPConfig,
    NormalizeConfig,
)
from .pipeline import VoiceEnhancePipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="voice-enhance",
        description="Studio-Grade Voice Enhancement Pipeline — Denoise → Restore → DSP → Normalize",
    )
    p.add_argument("input", type=str, help="Input audio file")
    p.add_argument("-o", "--output", type=str, help="Output audio file")
    p.add_argument("--sr", type=int, default=48000, help="Target sample rate (default: 48000)")
    p.add_argument("--output-dir", type=str, default="output", help="Output directory")

    g_denoise = p.add_argument_group("Denoise")
    g_denoise.add_argument("--no-denoise", action="store_false", dest="denoise_enabled")
    g_denoise.add_argument(
        "--denoise-engine",
        choices=["deepfilternet", "resemble"],
        default="deepfilternet",
    )

    g_restore = p.add_argument_group("Restore")
    g_restore.add_argument("--no-restore", action="store_false", dest="restore_enabled")
    g_restore.add_argument(
        "--restore-engine",
        choices=["voicefixer"],
        default="voicefixer",
    )

    g_dsp = p.add_argument_group("DSP")
    g_dsp.add_argument("--no-dsp", action="store_false", dest="dsp_enabled")
    g_dsp.add_argument("--hpf-cutoff", type=float, default=80.0)
    g_dsp.add_argument("--deesser-threshold", type=float, default=-20.0)
    g_dsp.add_argument("--comp-threshold", type=float, default=-18.0)
    g_dsp.add_argument("--comp-ratio", type=float, default=3.0)
    g_dsp.add_argument("--makeup-gain", type=float, default=2.0)
    g_dsp.add_argument("--limiter-threshold", type=float, default=-1.0)

    g_norm = p.add_argument_group("Normalize")
    g_norm.add_argument("--no-normalize", action="store_false", dest="normalize_enabled")
    g_norm.add_argument("--target-lufs", type=float, default=-16.0)
    g_norm.add_argument("--true-peak-limit", type=float, default=-1.0)

    p.add_argument("--keep-intermediate", action="store_true")
    p.add_argument("--verbose", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = PipelineConfig(
        sample_rate=args.sr,
        denoise=DenoiseConfig(
            enabled=args.denoise_enabled,
            engine=args.denoise_engine,
        ),
        restore=RestoreConfig(
            enabled=args.restore_enabled,
            engine=args.restore_engine,
        ),
        dsp=DSPConfig(
            enabled=args.dsp_enabled,
            highpass_cutoff=args.hpf_cutoff,
            deesser_threshold=args.deesser_threshold,
            comp_threshold=args.comp_threshold,
            comp_ratio=args.comp_ratio,
            makeup_gain=args.makeup_gain,
            limiter_threshold=args.limiter_threshold,
        ),
        normalize=NormalizeConfig(
            enabled=args.normalize_enabled,
            target_lufs=args.target_lufs,
            true_peak_limit=args.true_peak_limit,
        ),
        output_dir=args.output_dir,
        keep_intermediate=args.keep_intermediate,
    )

    pipeline = VoiceEnhancePipeline(config)
    try:
        result = pipeline.process_file(args.input, args.output)
        print(f"Done: {result}")
        return 0
    except Exception as e:
        logging.error("Pipeline failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
