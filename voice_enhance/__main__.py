import sys
from . import enhance

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: python -m voice_enhance input.wav [output.wav] [--key value ...]")
        sys.exit(1)

    inp = args[0]
    out = None
    kwargs = {}

    i = 1
    while i < len(args):
        if args[i].startswith("--"):
            k = args[i].lstrip("-").replace("-", "_")
            v = args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("--") else True
            kwargs[k] = v
            i += 2 if v is not True else 1
        else:
            out = args[i]
            i += 1

    result = enhance(inp, out, **kwargs)
    print(result)
