#!/usr/bin/env python3
"""
enhance.py — GitHub Actions script to enhance audio files via Adobe Podcast
using Playwright browser automation.

Usage:
    python enhance.py --input-dir <dir> --output-dir <dir> --auth-json <json>
"""

import argparse
import glob
import json
import os
import sys
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
ENHANCE_URL = "https://podcast.adobe.com/enhance"
UPLOAD_INPUT_SELECTOR = "#enhance-file-upload"
DOWNLOAD_BUTTON_SELECTOR = "[data-testid='download-button']"
MAX_WAIT_SECONDS = 300  # 5 minutes
DEFAULT_DOWNLOAD_DIR = "/tmp/adobe_downloads"

SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".oga", ".aac",
    ".mp4", ".m4v", ".mov", ".3gp", ".webm", ".3gpp"
}


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def get_audio_files(input_dir: str) -> list[str]:
    """Find all supported audio/video files in input_dir."""
    files = []
    for entry in sorted(os.listdir(input_dir)):
        ext = Path(entry).suffix.lower()
        if ext in SUPPORTED_EXTENSIONS:
            files.append(os.path.join(input_dir, entry))
    return files


def extract_ext(filepath: str) -> str:
    """Return the original file extension (including dot)."""
    return Path(filepath).suffix


def build_output_name(original_name: str) -> str:
    """Return enhanced_<original_name>."""
    p = Path(original_name)
    return f"enhanced_{p.name}"


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def write_status(output_dir: str, results: dict) -> None:
    """Write a JSON status file summarising results."""
    path = os.path.join(output_dir, "results.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log(f"Status written to {path}")


# ──────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────

def enhance_file(
    page,
    filepath: str,
    output_dir: str,
    base_download_dir: str,
) -> dict:
    """
    Upload a single file to Adobe Podcast, wait for processing,
    download the enhanced version, and return a result dict.
    """
    filename = os.path.basename(filepath)
    output_name = build_output_name(filename)
    output_path = os.path.join(output_dir, output_name)
    result = {
        "file": filename,
        "status": "unknown",
        "output": None,
        "error": None,
    }

    log(f"▶ Processing: {filename}")

    try:
        # ── Navigate to enhance page ──
        log(f"  Navigating to {ENHANCE_URL} …")
        page.goto(ENHANCE_URL, wait_until="domcontentloaded", timeout=60_000)
        # Extra wait for React/Vue hydration
        page.wait_for_timeout(3_000)

        # ── Upload the file ──
        log(f"  Uploading {filename} …")
        upload_input = page.locator(UPLOAD_INPUT_SELECTOR)
        upload_input.set_input_files(filepath)
        log("  File uploaded, waiting for processing …")

        # ── Wait for download button ──
        log(f"  Waiting up to {MAX_WAIT_SECONDS}s for download button …")
        try:
            download_btn = page.locator(DOWNLOAD_BUTTON_SELECTOR)
            download_btn.wait_for(state="visible", timeout=MAX_WAIT_SECONDS * 1_000)
            log("  Download button is visible!")
        except PlaywrightTimeout:
            result["status"] = "timeout"
            result["error"] = f"Download button did not appear within {MAX_WAIT_SECONDS}s"
            log(f"  ✗ TIMEOUT: {result['error']}")
            return result

        # ── Determine download destination ──
        # Ensure clean download directory
        os.makedirs(base_download_dir, exist_ok=True)

        # ── Click download and capture the file ──
        with page.expect_download(timeout=120_000) as download_info:
            download_btn.click()

        download = download_info.value
        log(f"  Download started: {download.suggested_filename}")
        download.save_as(output_path)
        log(f"  Saved to: {output_path}")

        # ── Verify ──
        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            result["status"] = "success"
            result["output"] = output_name
            log(f"  ✓ Successfully enhanced: {output_name} "
                f"({os.path.getsize(output_path) / (1024*1024):.2f} MB)")
        else:
            result["status"] = "error"
            result["error"] = "Downloaded file is empty or missing"
            log(f"  ✗ Downloaded file is empty or missing")

    except PlaywrightTimeout as e:
        result["status"] = "timeout"
        result["error"] = str(e)
        log(f"  ✗ PlaywrightTimeout: {e}")
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"{type(e).__name__}: {e}"
        log(f"  ✗ Exception: {e}")
        traceback.print_exc()

    # ── Cleanup original ──
    if os.path.isfile(filepath):
        os.remove(filepath)
        log(f"  Cleaned up original: {filename}")

    return result


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enhance audio files via Adobe Podcast using Playwright."
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="Directory containing audio files to enhance."
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory where enhanced files will be saved."
    )
    parser.add_argument(
        "--auth-json", required=True,
        help="Path to auth.json (Playwright storage state)."
    )
    args = parser.parse_args()

    # ── Validate inputs ──
    if not os.path.isdir(args.input_dir):
        log(f"FATAL: input directory not found: {args.input_dir}")
        sys.exit(1)
    if not os.path.isfile(args.auth_json):
        log(f"FATAL: auth.json not found: {args.auth_json}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    audio_files = get_audio_files(args.input_dir)
    if not audio_files:
        log("No audio files found in input directory. Nothing to do.")
        write_status(args.output_dir, {"files": [], "summary": "no_files"})
        sys.exit(0)

    log(f"Found {len(audio_files)} file(s) to process.")

    results = {"files": [], "summary": None}
    download_base = DEFAULT_DOWNLOAD_DIR
    os.makedirs(download_base, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        context = browser.new_context(
            storage_state=args.auth_json,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )

        page = context.new_page()
        page.set_default_timeout(120_000)

        for filepath in audio_files:
            result = enhance_file(
                page, filepath, args.output_dir, download_base
            )
            results["files"].append(result)

            # If enhancement failed, try navigating back to start fresh
            if result["status"] not in ("success",):
                try:
                    page.goto(ENHANCE_URL, wait_until="domcontentloaded", timeout=30_000)
                    page.wait_for_timeout(2_000)
                except Exception:
                    log("  Warning: Could not reset page after failure.")

        browser.close()

    # ── Summary ──
    success_count = sum(1 for r in results["files"] if r["status"] == "success")
    fail_count = len(results["files"]) - success_count
    results["summary"] = {
        "total": len(results["files"]),
        "success": success_count,
        "failed": fail_count,
    }
    log(f"\n{'='*50}")
    log(f"SUMMARY: {success_count} succeeded, {fail_count} failed "
        f"out of {len(results['files'])} file(s).")

    write_status(args.output_dir, results)


if __name__ == "__main__":
    main()
