# Archive-downloader

Archive-downloader is a python package for downloading files on archive.org.


## Usage

Everything is done through the ArchiveDownloader class.
To initate, simply use the URL and the destination directory as input.

```
from archive_downloader import ArchiveDownloader

input_url = 'https://archive.org/details/KSC-KSC-69P-168'    # Both details/ and download/ are supported
download_directory_path = '~/Desktop/download'

test_dl = ArchiveDownloader(input_url[str], download_directory_path[str])
```

To download the files:
```
test_dl.get()
```

You should find a photo of the S-1C booster for the Apollo 11 Saturn V in the destination directory.

<!--
## To-do

* Complete the test cases -->

