# Archive-downloader

Archive-downloader is a small Python utility for downloading files from archive.org item pages. It uses `requests` and Beautiful Soup 4 to extract file links from archive.org HTML, and uses `wget` to download the files.

## Requirements

This project depends on:

- Python 3
- `requests`
- `beautifulsoup4`
- `pandas`
- `lxml`
- `wget` installed on your system and available on `PATH`

Install the Python libraries with:

```bash
pip install requests beautifulsoup4 pandas lxml
```

## Usage

Everything is done through the `ArchiveDownloader` class.
To initialize it, pass an archive.org item URL and a destination directory.

```python
from archive_downloader import ArchiveDownloader

# Both /details/ and /download/ are supported:
input_url = 'https://archive.org/details/KSC-KSC-69P-168'  # Str

download_directory_path = '~/Desktop/download'  # Str

test_dl = ArchiveDownloader(input_url, download_directory_path)
```

To download all the files:

```python
test_dl.get()
```

You should find this photo of the S-1C booster for the Apollo 11 Saturn V rocket in the specified destination directory.

<img src="https://ia600205.us.archive.org/32/items/KSC-KSC-69P-168/KSC-69P-168.jpg" width="400">


To download only some files by extension, first generate a configuration file:

```python
test_dl.generate_config_file(filename='test_dl.config')
# Default filename is archive_downloader.config
```

This creates a tab-separated config file in the download directory listing all discovered files. By default, files are marked as not selected for download (`N`). You can change that by setting `default_download=True`.

To select files by their file extension and download them:

```python
test_dl.edit_config_file('extension', 'jpg', set_download=True, filename='test_dl.config')
test_dl.get(config_file='test_dl.config')
```

Only .jpg files will be downloaded to the specified destination directory.

## CLI

The repository also supports a simple CLI through `archive_downloader.py`.

List downloadable files:

```bash
python archive_downloader.py list "https://archive.org/details/KSC-KSC-69P-168"
```

Generate a config file and pre-select one extension:

```bash
python archive_downloader.py config \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --config-file photos.config \
  --extension jpg
```

Download files directly by extension:

```bash
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --extension jpg
```

Download using an existing config file:

```bash
python archive_downloader.py download \
  "https://archive.org/details/KSC-KSC-69P-168" \
  ~/Desktop/download \
  --config-file photos.config
```

## Project Layout

- `archive_downloader.py`: main downloader implementation
- `notebooks/`: local notebooks kept for exploration and reference



## To-do

* <del>Add a configuration file option to let the user to download only some of the files in the URL.</del> (Done!)


## Known Issues

* Archive-downloader has some issues dealing with filenames that have Unicode characters. `wget` can throw an illegal byte sequence error when saving the file. One workaround is to adjust the `LC_CTYPE` and `LANG` variables in the shell.
