# Archive-downloader

Archive-downloader is a simple downloader for downloading files on achive.org.


## Usage

Everything is done through the ArchiveDownloader class. To initate, simply use the URL and the destination directory as input
```
from archive_downloader import ArchiveDownloader

input_url = 'https://archive.org/details/KSC-KSC-69P-168'
download_directory_path = '~/Desktop/download'

test_dl = ArchiveDownloader(input_url[str], download_directory_path[str])
```

To download the files:
```
test_dl.get()
```
<!--
## To-do

* Complete the test cases -->

