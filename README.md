# Archive-downloader

Archive-downloader is a python package for downloading files on archive.org. It uses Beautiful Soup 4 and wget to extract links from the HTML and download the files.


## Usage

Everything is done through the ArchiveDownloader class.
To initate, simply use the URL and the destination directory as input.

```
from archive_downloader import ArchiveDownloader

# Both /details/ and /download/ are supported:
input_url = 'https://archive.org/details/KSC-KSC-69P-168'  # Str

download_directory_path = '~/Desktop/download'  # Str

test_dl = ArchiveDownloader(input_url, download_directory_path)
```

To download the files:
```
test_dl.get()
```

You should find this photo of the S-1C booster for the Apollo 11 Saturn V rocket in the specified destination directory.

<img src="https://ia600205.us.archive.org/32/items/KSC-KSC-69P-168/KSC-69P-168.jpg" width="400">


## To-do

* Add a configuration option to let the user to download only some of the files in the URL.


