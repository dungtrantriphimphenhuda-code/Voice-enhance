# Voice Enhance

[Audio Gốc] → [Denoise] → [Restore] → [DSP] → [Normalize] → [Output Studio]

## Usage

```bash
pip install -r requirements.txt
python -m voice_enhance input.wav output.wav
```

### Python API

```python
from voice_enhance import enhance
enhance("input.wav", "output.wav")

# Tuy chinh
enhance("input.wav", "output.wav", denoise_engine="resemble", target_lufs=-14)
```

### Google Colab

Open `colab.py` and copy into a single cell.

### GitHub Actions

```yaml
# .github/workflows/enhance.yml
name: Enhance Audio
on: [workflow_dispatch]
jobs:
  enhance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python -m voice_enhance input.wav output.wav
      - uses: actions/upload-artifact@v4
        with:
          name: enhanced
          path: output.wav
```

## Toggle stages

```bash
python -m voice_enhance input.wav --no-restore --no-dsp
python -m voice_enhance input.wav --denoise_engine resemble
python -m voice_enhance input.wav --target_lufs -14
```

MIT
