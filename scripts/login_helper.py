#!/usr/bin/env python3
"""
login_helper.py — One-time helper to log into Adobe Podcast
and save the browser state (auth.json) for reuse in CI.

Usage:
    python login_helper.py

After running, auth.json will be saved in the current directory.
Copy its contents to a GitHub repository secret named AUTH_JSON.
"""

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


SAVE_PATH = "auth.json"
LOGIN_URL = "https://podcast.adobe.com/enhance"


def main():
    print("=" * 60)
    print("Adobe Podcast — Auth JSON Generator")
    print("=" * 60)
    print(f"Will open a browser window. Please log in to Adobe Podcast.")
    print(f"Once logged in, come back here and press ENTER.")
    print()

    with sync_playwright() as pw:
        # Launch headed browser so you can interact with it
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = context.new_page()

        # Navigate to Adobe Podcast
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        print(f"Browser opened. Navigate to: {LOGIN_URL}")
        print("Log in with your Adobe account.")
        print("Make sure you can see the 'Choose files' button on the page.")

        # Wait for user
        input("\nPress ENTER when you are done logging in and can see the enhance page...")

        # Wait a moment for all cookies/storage to settle
        page.wait_for_timeout(3_000)

        # Save storage state
        context.storage_state(path=SAVE_PATH)
        print(f"\n✓ Auth state saved to: {os.path.abspath(SAVE_PATH)}")

        browser.close()

    # Verify
    try:
        with open(SAVE_PATH) as f:
            data = json.load(f)
        cookie_count = len(data.get("cookies", []))
        storage_count = len(data.get("origins", []))
        print(f"  - {cookie_count} cookies saved")
        print(f"  - {storage_count} storage origins saved")
    except Exception as e:
        print(f"✗ Could not verify: {e}")

    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("  1. Copy the contents of auth.json")
    print("  2. In your GitHub repo: Settings → Secrets and variables → Actions")
    print("  3. Add a new repository secret named AUTH_JSON")
    print("  4. Paste the contents of auth.json as the value")
    print("=" * 60)


if __name__ == "__main__":
    main()
