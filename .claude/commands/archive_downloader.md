Help the user work with the archive_downloader CLI in this project.

The CLI entry point is `archive_downloader.py` in the project root. All commands follow this structure:

```
python archive_downloader.py <command> [args] [options]
```

## Available commands

### `list` – Inspect files before downloading

```bash
python archive_downloader.py list "<archive.org-url>"
# Optionally specify a working directory (defaults to current dir):
python archive_downloader.py list "<archive.org-url>" --save-dir "<dir>"
```

### `config` – Generate a config file to selectively mark files for download

The config file is written into `<save-dir>`.

```bash
# Basic: generate config with all files set to N (not selected)
python archive_downloader.py config "<archive.org-url>" "<save-dir>"

# Custom config filename (default: archive_downloader.config)
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --config-file my.config

# Mark all files Y, then manually deselect what you don't want
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --default-download

# "Download everything except these extensions" pattern:
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --default-download --exclude-extension xml --exclude-extension sqlite

# "Download only these extensions" pattern:
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --extension jpg --extension png

# Combine include and exclude (include runs first, then exclude overrides):
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --extension jpg --exclude-extension xml
```

### `download` – Download files

`<save-dir>` is created automatically if it does not exist. After downloading, the tool reports any files that are still missing.

```bash
# Download everything
python archive_downloader.py download "<archive.org-url>" "<save-dir>"

# Filter by extension (can be repeated)
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --extension jpg --extension png

# Use a config file (honours Y/N selections)
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config

# Combine: --extension pre-filters the list, then --config-file further narrows it
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --extension jpg --config-file archive_downloader.config

# Suppress curl progress output
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --extension jpg --quiet
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config --quiet
```

## Recommended workflows

**Simple extension-based download** (no config file needed):
1. `list` to see what's available.
2. `download` with `--extension` to grab specific file types.

**Selective download via config file:**
1. `list` to see what's available.
2. `config` to generate a config file (optionally pre-select with `--default-download`, `--extension`, `--exclude-extension`).
3. Edit the config file manually: set `Y` or `N` in the `Download` column.
4. `download --config-file` to download only the selected files.

## Flag reference

| Command | Flag | Description |
|---------|------|-------------|
| `list` | `--save-dir <dir>` | Working directory (default: `.`) |
| `config` | `--config-file <name>` | Config filename (default: `archive_downloader.config`) |
| `config` | `--default-download` | Mark all files `Y`; default is all `N` |
| `config` | `--extension <ext>` | Mark matching files `Y`; repeatable |
| `config` | `--exclude-extension <ext>` | Mark matching files `N`; repeatable |
| `download` | `--config-file <name>` | Use config file to select files |
| `download` | `--extension <ext>` | Pre-filter to these extensions; repeatable |
| `download` | `--quiet` | Suppress curl verbose output |

## Notes

- Both `/details/` and `/download/` archive.org URLs are accepted.
- Extensions can be passed with or without the dot (`.jpg` and `jpg` are both valid).
- When `--extension` and `--config-file` are both passed to `download`, extension filtering is applied first, then the config file further narrows the list.
- The config file is always written to and read from `<save-dir>`.
- After each download run, the tool automatically reports any files that were expected but are still missing.
- `curl` must be on `PATH` for `config` and `download` commands (`list` does not require it).

## Setup

```bash
pip install -r requirements.txt   # requests, beautifulsoup4, lxml, pandas
# Also ensure curl is on PATH
```

Now help the user with their specific archive_downloader request: $ARGUMENTS
