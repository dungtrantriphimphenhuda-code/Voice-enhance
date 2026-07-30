import numpy as np, soundfile as sf, tempfile, os
from voice_enhance import enhance

def _gen(sr=48000, d=2.0):
    t = np.linspace(0, d, int(sr*d), endpoint=False)
    return (0.5*np.sin(2*np.pi*440*t) + 0.05*np.random.randn(len(t))).astype(np.float32)

def test_enhance_defaults():
    a = _gen()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, a, 48000); inp = f.name
    out = inp.replace(".wav", "_out.wav")
    try:
        r = enhance(inp, out)
        assert os.path.exists(r)
        data, sr = sf.read(r)
        assert sr == 48000 and len(data) and not np.any(np.isnan(data))
        assert np.all(np.abs(data) <= 1.0)
    finally:
        for p in [inp, out]:
            os.path.exists(p) and os.unlink(p)

def test_enhance_disabled():
    a = _gen()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, a, 48000); inp = f.name
    out = inp.replace(".wav", "_out.wav")
    try:
        r = enhance(inp, out, denoise=False, restore=False, dsp=False, normalize=False)
        orig, _ = sf.read(inp)
        res, _ = sf.read(r)
        assert np.allclose(orig, res, atol=1e-6)
    finally:
        for p in [inp, out]:
            os.path.exists(p) and os.unlink(p)
