def enhance(input_path: str, output_path: str | None = None, **kwargs) -> str:
    from ._pipeline import run
    return run(input_path, output_path, kwargs)
