# Archive Downloader Workflow

This repository includes a small CLI for listing, configuring, and downloading files from archive.org item pages.

## Commands

List files from an archive.org item:

```bash
python archive_downloader.py list "<archive.org-url>"
```

Create a config file:

```bash
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config
```

Create a config file and preselect extensions:

```bash
python archive_downloader.py config "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config --extension jpg
```

Download by extension:

```bash
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --extension jpg
```

Download with an existing config file:

```bash
python archive_downloader.py download "<archive.org-url>" "<save-dir>" --config-file archive_downloader.config
```

## Environment

- Install Python dependencies with `pip install -r requirements.txt`
- Ensure `wget` is installed and available on `PATH`

## Notes

- Supported inputs are archive.org `/details/` and `/download/` URLs.
- Prefer `list` before `download` when you want to inspect files first.
