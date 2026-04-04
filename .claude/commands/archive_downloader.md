Help the user work with the archive_downloader CLI in this project.

The CLI entry point is `archive_downloader.py` in the project root. All commands follow this structure:

```
python archive_downloader.py <command> [args] [options]
```

## Available commands

**list** – Inspect files available for download before committing to anything.
```bash
python archive_downloader.py list "<archive.org-url>"
```

**config** – Generate a config file to selectively mark files for download.
```bash
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config
# Pre-select extensions when creating the config:
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --extension jpg --extension png
```

**download** – Download files, optionally filtered by extension or config file.
```bash
# By extension:
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --extension jpg
# Using a config file:
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config
```

## Recommended workflow

1. Run `list` to see what files are available.
2. Run `config` to generate a config file, optionally pre-selecting extensions.
3. Edit the config file manually if needed (set `Y`/`N` in the Download column).
4. Run `download` with `--config-file` to download only selected files.

## Setup

```bash
pip install -r requirements.txt   # Python deps (requests, beautifulsoup4, lxml, pandas)
# Also ensure curl is on PATH
```

## Notes

- Both `/details/` and `/download/` archive.org URLs are accepted.
- `--extension` can be repeated for multiple extensions (e.g. `--extension jpg --extension xml`).
- `--quiet` suppresses curl verbose output during download.

Now help the user with their specific archive_downloader request: $ARGUMENTS
