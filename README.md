1. **Parse** — Reads the HTML catalog exported from NASA's search tool and extracts photo IDs via regex
2. **Build URLs** — Constructs direct links to high-res images on NASA's JSC server
3. **Download** — Fetches photos in parallel using `ThreadPoolExecutor` with a live ETA in the terminal

## Quick start

```bash
pip install requests
```

1. Clone or download this repository
2. Run:

```bash
python artemis_downloader.py
```

## Configuration

Edit the top of `artemis_downloader.py`:

| Variable | Description | Default |
|---|---|---|
| `CATALOG_HTML` | Path to the exported HTML catalog | `catalog.html` |
| `OUTPUT_DIR` | Where to save downloaded photos | `./artemis_ii_photos/` |
| `MAX_WORKERS` | Parallel download threads | `10` |


## Note

This script is intentionally throttled to 10 concurrent connections. Be respectful with NASA's servers — they're serving this data for free and for everyone.

## License

MIT
