# Archive-downloader

Archive-downloader is a python package for downloading files on archive.org. It uses Beautiful Soup 4 and wget to extract links from the HTML and download the files.

## Requirement

This script uses pandas and Beautiful Soup 4. To install the libraries:  
``` pip install bs4 pandas```

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

To download all the files:
```
test_dl.get()
```

You should find this photo of the S-1C booster for the Apollo 11 Saturn V rocket in the specified destination directory.

<img src="https://ia600205.us.archive.org/32/items/KSC-KSC-69P-168/KSC-69P-168.jpg" width="400">


To download only some of files by file extension, first uses the generate_config_file method to generate a configuration file:
```
test_dl.generate_config_file(filename='test_dl.config')
# Default filename is archive_downloader.config
```

This will generate a config file listing all the files to be downloaded. The default is not to download any files ('N').
This can be changed by setting default_download=True above.

To select files by their file extension and download them:

```
test_dl.edit_config_file('extension', 'jpg', set_download=True, filename='test_dl.config')
test_dl.get(config_file='test_dl.config')
```

Only .jpg files will be downloaded to the specified destination directory.



## To-do

* <del>Add a configuration file option to let the user to download only some of the files in the URL.</del> (Done!)


## Known Issues

* Archive-downloader has some issues dealing with filenames that have Unicode characters. wget will throw an illegal byte sequence error when saving the file. To deal with this, one can change the LC_CTYPE and LANG variables of the shell.


