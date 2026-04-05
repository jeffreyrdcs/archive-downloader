# Archive-downloader

Archive-downloader is a small Python utility for downloading files from archive.org item pages. It uses `requests` and Beautiful Soup 4 to extract file links from archive.org HTML, and `curl` to download files.

## Requirements

- Python 3
- `requests`
- `beautifulsoup4`
- `pandas`
- `lxml`
- `curl` installed on your system and available on `PATH`

Install the Python libraries with:

```bash
pip install -r requirements.txt
```

## CLI

The primary way to use archive-downloader is through the CLI.

### List files

Inspect what's available before downloading:

```bash
python archive_downloader.py list "https://archive.org/details/KSC-KSC-69P-168"

# Optionally specify a working directory (defaults to current dir):
python archive_downloader.py list "https://archive.org/details/KSC-KSC-69P-168" --save-dir ~/Desktop/download
```

### Generate a config file

The config file lets you mark individual files for download (`Y`/`N`) before running. It is written into `<save-dir>`.

```bash
# All files default to N — edit the file to select what you want
python archive_downloader.py config \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --config-file photos.config

# Mark all files Y upfront, then deselect what you don't want
python archive_downloader.py config \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --default-download

# "Download everything except these extensions" pattern
python archive_downloader.py config \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --default-download \
  --exclude-extension xml \
  --exclude-extension sqlite

# "Download only these extensions" pattern
python archive_downloader.py config \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --extension jpg \
  --extension png
```

### Download files

```bash
# Download everything
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download

# Filter by extension directly (no config file needed)
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --extension jpg

# Use a config file
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --config-file photos.config

# Combine: --extension pre-filters the list, then --config-file narrows further
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --extension jpg \
  --config-file photos.config

# Suppress curl progress output
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --extension jpg \
  --quiet
```

After downloading, the tool automatically reports any expected files that are still missing.

### Flag reference

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

### Recommended workflow

1. Run `list` to see what files are available.
2. Run `config` to generate a config file (use `--default-download`, `--extension`, or `--exclude-extension` to pre-populate selections).
3. Edit the config file manually if needed — set `Y` or `N` in the `Download` column.
4. Run `download --config-file` to download only the selected files.

## Python API

You can also use the `ArchiveDownloader` class directly:

```python
from archive_downloader import ArchiveDownloader

# Both /details/ and /download/ URLs are supported
input_url = 'https://archive.org/details/KSC-KSC-69P-168'
download_directory_path = '~/Desktop/download'

dl = ArchiveDownloader(input_url, download_directory_path)

# Download all files
dl.get()

# Or generate a config file first
dl.generate_config_file(filename='photos.config')           # all N by default
dl.generate_config_file(default_download=True, filename='photos.config')  # all Y

# Select / deselect by extension
dl.edit_config_file('extension', 'jpg', set_download=True, filename='photos.config')
dl.edit_config_file('extension', 'xml', set_download=False, filename='photos.config')

# Download using the config
dl.get(config_file='photos.config')

# Or filter in-memory by extension and download
dl.select_extensions(['jpg', 'png'])
dl.get()

# List discovered files without downloading
for f in dl.list_files():
    print(f)
```

## Project Layout

- `archive_downloader.py` — main downloader implementation and CLI entry point
- `requirements.txt` — Python dependencies
- `notebooks/` — local notebooks kept for exploration and reference

## Notes

- Both `/details/` and `/download/` archive.org URLs are accepted.
- Extensions can be passed with or without the leading dot (`.jpg` and `jpg` are both valid).
- `<save-dir>` is created automatically if it does not exist.
