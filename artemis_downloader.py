"""
Artemis II — NASA Astronaut Photography Bulk Downloader

Downloads high-resolution photos taken by Artemis II astronauts from NASA's
Gateway to Astronaut Photography of Earth (eol.jsc.nasa.gov).

Usage:
    pip install requests
    python artemis_downloader.py
"""

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests

# ─── Configuration ───────────────────────────────────────────────────────────

CATALOG_HTML = "catalog.html"
OUTPUT_DIR   = "./artemis_ii_photos/"
MAX_WORKERS  = 10

NASA_BASE_URL = "https://eol.jsc.nasa.gov/DatabaseImages/ESC/large"
PHOTO_ID_PATTERN = re.compile(r">([A-Z0-9]+-[A-Z0-9]+-\d+)</a>")


# ─── Core ────────────────────────────────────────────────────────────────────

def extract_photo_ids(html_path: str) -> list[str]:
    """Parse the NASA catalog HTML and return unique photo IDs."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    ids = list(set(PHOTO_ID_PATTERN.findall(html)))

    if not ids:
        raise ValueError(f"No photo IDs found in '{html_path}'.")

    return ids


def download_photo(photo_id: str) -> tuple[str, str]:
    """Download a single photo. Returns (status, photo_id)."""
    mission = photo_id.split("-")[0]
    url = f"{NASA_BASE_URL}/{mission}/{photo_id}.JPG"
    dest = os.path.join(OUTPUT_DIR, f"{photo_id}.JPG")

    if os.path.exists(dest):
        return "skip", photo_id

    try:
        resp = requests.get(url, stream=True, timeout=15)
        resp.raise_for_status()

        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return "ok", photo_id

    except requests.HTTPError:
        return f"http_{resp.status_code}", photo_id
    except requests.RequestException:
        return "error", photo_id


def format_eta(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m:02d}m"


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    photo_ids = extract_photo_ids(CATALOG_HTML)
    total = len(photo_ids)
    print(f"[artemis] {total} photos found. Starting download.\n")

    start = time.time()
    ok, skipped, failed = 0, 0, 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i, (status, pid) in enumerate(pool.map(download_photo, photo_ids), 1):
            elapsed = max(time.time() - start, 0.001)
            eta = format_eta((total - i) / (i / elapsed))

            if status == "ok":
                ok += 1
            elif status == "skip":
                skipped += 1
            else:
                failed += 1
                print(f"\n  FAIL  {pid} ({status})")

            print(f"\r[{i}/{total} | ETA {eta}] ok:{ok} skip:{skipped} fail:{failed}", end="", flush=True)

    elapsed_total = time.time() - start
    print(f"\n\n[artemis] Done in {format_eta(elapsed_total)}. "
          f"Downloaded: {ok} | Skipped: {skipped} | Failed: {failed}")


if __name__ == "__main__":
    main()
