import argparse
import os
import shutil
import sys
from urllib.parse import unquote


def require_dependency(name, import_name=None):
    """Import a dependency lazily so CLI help still works without the package installed."""
    module_name = import_name or name
    try:
        return __import__(module_name)
    except ModuleNotFoundError:
        print(
            f"Missing dependency: {module_name}. Install project requirements before running this command.",
            file=sys.stderr,
        )
        sys.exit(2)


class ArchiveDownloader:
    """
    ArchiveDownloader class.
    """
    def __init__(self, input_url, save_dir, wget_verbose=True):
        """
        Constructor. Take input URL and the directory path for saving the files
        """
        self.download_url = ''
        self.download_link_list = []
        self.count = 0
        self.input_url = input_url
        self.save_dir = os.path.abspath(self.replace_tilde_path(save_dir))    # Replace ~ in the input path
        self.ensure_save_dir()

        # Verbose flag
        if wget_verbose:
            self.wget_verbose = 1  # Default
        else:
            self.wget_verbose = 0

        if self.check_download_availabilty():
            self.download_url = input_url.replace('/details/', '/download/')
            self.download_link_list = self.get_download_list()
            self.count = len(self.download_link_list)
            print('URL list ready. Use .get to start download')
        else:
            print('The URL is not compatible with this downloader.')
            sys.exit(3)

    def ensure_save_dir(self):
        """Create the save directory when it does not exist."""
        os.makedirs(self.save_dir, exist_ok=True)


    def check_download_availabilty(self):
        """
        Check if the archive url has a download option
        """
        if 'archive.org' not in self.input_url:
            print('Not a valid archive.org URL!')
            return False

        # If the input URL is already the download page
        if 'download' in self.input_url:
            return True

        # If it is the detail page, look for the download options and download button class
        requests = require_dependency('requests')
        bs4 = require_dependency('beautifulsoup4', 'bs4')
        result = requests.get(self.input_url)
        front_soup = bs4.BeautifulSoup(result.text,"lxml")
        first_test = front_soup.select('.item-download-options')
        second_test = front_soup.select('.download-button')

        return len(first_test) > 0 and len(second_test) > 0


    def get_download_list(self):
        """
        Get a list of to-be-downloaded URLs
        """
        requests = require_dependency('requests')
        bs4 = require_dependency('beautifulsoup4', 'bs4')
        dresult = requests.get(self.download_url)
        download_soup = bs4.BeautifulSoup(dresult.text,"lxml")
        download_list = download_soup.find_all('a', href=True)

        return self.filter_download_list(download_list)

    def list_files(self):
        """Return the current download list as decoded file names."""
        return [unquote(item) for item in self.download_link_list]


    def filter_download_list(self, download_list):
        """ Clean up the download list """
        download_href_list = []

        for item in download_list:
            tmp_href = item['href']
            # print("Found URL:", tmp_href)
            download_href_list.append(item['href'])

        download_href_list = list(filter(lambda h: h[-1] != '/', download_href_list))  # Remove directory href
        download_href_list = list(filter(lambda h: h[0] != '#', download_href_list))   # Remove page href
        download_href_list = list(filter(lambda h: h[0] != '/' and
                                    h[0:8] != 'https://', download_href_list))     # Remove archive.org href
        download_href_list = list(filter(lambda h: '.' in h, download_href_list))  # only grab files with .extension

        # download_href_list = list(filter(lambda h: h[0] != '%', download_href_list)) # Remove files begin with %, those could be URL encoded
        # download_href_list = [unquote(h) if h[0] == '%' else h for h in download_href_list] # If file start with %, could be URL encoded

        # Convert it to the full URL (Currently not implemented due to how check_save_dir works)
        # download_href_list = [self.download_url+'/'+h for h in download_href_list]
        return download_href_list


    def replace_tilde_path(self, in_save_dir):
        """ Replace the ~ symbol to $HOME env variable """
        return in_save_dir.replace('~', os.getenv('HOME'))

    def select_extensions(self, extensions):
        """Keep only files whose extension matches the requested list."""
        normalized = {ext.lower().lstrip('.') for ext in extensions}
        self.download_link_list = [
            item for item in self.download_link_list
            if item.split('.')[-1].lower() in normalized
        ]
        self.count = len(self.download_link_list)


    def get_save_dir_file_list(self):
        """ Get the file list of the save directory """
        os.chdir(self.save_dir)
        save_dir_file_list = os.listdir()
        save_dir_file_list = list(filter(lambda h: h[0] != '.', save_dir_file_list))

        return save_dir_file_list


    def compare_save_list_download_list(self):
        """ Compare the download_link_list with the file list in the directory """
        in_save_list = self.get_save_dir_file_list()
        download_list_unquote = [unquote(h) for h in self.download_link_list]   # Need to unquote (decode) the URL

        return set(download_list_unquote).symmetric_difference(set(in_save_list))


    def generate_config_header(self, filename):
        """ Write the header of the config file. Overwrite existing file """
        with open(filename, 'w') as f:
            f.write("=" * 80+'\n')
            f.write("    ArchiveDownloader Configuration File"+'\n')
            f.write("=" * 80+'\n')


    def generate_config_file(self, default_download=False, filename='archive_downloader.config'):
        """
        Generate a config file based on the download link list. Write the config file to the save dir.
        Also return a pd dataframe of the config file (currently removed)
        """
        pd = require_dependency('pandas')
        os.chdir(self.save_dir)

        if default_download:
            dl_option_list = ['Y'] * len(self.download_link_list)
        else:
            dl_option_list = ['N'] * len(self.download_link_list)

        config_df = pd.DataFrame(zip(self.download_link_list, dl_option_list), columns=['File','Download'], index=list(range(1,self.count+1)))

        self.generate_config_header(filename)

        config_df.to_csv(filename, mode='a', sep='\t', index=True)
        print(f"[ArchiveDownloader] Generated config file {filename} to {self.save_dir}")
        # return config_df


    def process_config_file(self, filename='archive_downloader.config'):
        """
        Read an input config file and modify the download link list and count accordingly.
        Return a boolean status flag.
        """
        pd = require_dependency('pandas')
        try:
            config_df = pd.read_csv(self.save_dir+'/'+filename, sep='\t', skiprows=3, index_col=0)

            # Check if the download link list is a subset of the config file
            if set(self.download_link_list).issubset(set(config_df['File'])):
                # Check if config_df is all Y
                if sum(config_df['Download'] == 'N') == 0:
                    return True

                for (i, file) in config_df[config_df['Download'] == 'N'].iterrows():
                    if file['File'] in self.download_link_list:
                        self.download_link_list.remove(file['File'])

                self.count = len(self.download_link_list)
                return True

        except OSError:
            print("[ArchiveDownloader] Could not open config file")
            return False


    def edit_config_file(self, criteria, command, set_download=True, filename='archive_downloader.config'):
        """
        Edit the config file according to some criteria. Currently implemented:
        criteria=extension - select files with certain extension and set download to Y or N
        """
        pd = require_dependency('pandas')
        try:
            config_df = pd.read_csv(self.save_dir+'/'+filename, sep='\t', skiprows=3, index_col=0)

            if criteria == 'extension':
                # Extract all the file extension
                config_df['extension'] = config_df['File'].apply(lambda x: x.split('.')[-1])

                if set_download:
                    config_df.loc[config_df['extension'] == command,'Download'] = 'Y'
                else:
                    config_df.loc[config_df['extension'] == command,'Download'] = 'N'

                config_df = config_df.drop('extension', axis=1)
            else:
                # More critieria available soon.
                pass


            self.generate_config_header(filename)

            config_df.to_csv(self.save_dir+'/'+filename, mode='a', sep='\t', index=True)

        except OSError:
            print("[ArchiveDownloader] Could not open config file")
            return False


    def get(self, config_file=None):
        """
        Download the files from the list using wget. Let wget to handle all the incomplete files
        with the -continue and -N flag.
        If config_file is provided, will only download files with download set to Y.
        """
        os.makedirs(self.save_dir, exist_ok=True)
        os.chdir(self.save_dir)

        if config_file != None:
            if self.process_config_file(config_file):
                print(f'[ArchiveDownloader] Successfully process config file: {config_file}')
            else:
                print(f'[ArchiveDownloader] Skipping config file: {config_file}')

        print(f'[ArchiveDownloader] Downloading {self.count} files from {self.download_url} ...')

        for ind, file in enumerate(self.download_link_list):
            file_full_link = self.download_url +'/'+ file

            filename = unquote(file_full_link.split('/')[-1])
            if self.wget_verbose == 1:
                os.system(f'curl -L -C - -o {filename!r} {file_full_link!r}')
            else:
                os.system(f'curl -sS -L -C - -o {filename!r} {file_full_link!r}')

        check_set = self.compare_save_list_download_list()

        if len(check_set) == 0:
            print('\n')
            print(f'[ArchiveDownloader] All {self.count} files downloaded from {self.download_url}.\n')
        else:
            check_str = ', '.join(list(check_set))
            print(f"[ArchiveDownloader] Files that are still missing: {check_str}")


def build_parser():
    parser = argparse.ArgumentParser(
        description='List, configure, and download files from archive.org item pages.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    list_parser = subparsers.add_parser('list', help='List downloadable files for an archive.org item.')
    list_parser.add_argument('url', help='archive.org /details/ or /download/ URL')
    list_parser.add_argument(
        '--save-dir',
        default='.',
        help='Directory used for initialization. Defaults to the current directory.',
    )

    config_parser = subparsers.add_parser('config', help='Generate or update a download config file.')
    config_parser.add_argument('url', help='archive.org /details/ or /download/ URL')
    config_parser.add_argument('save_dir', help='Directory where files and config will live')
    config_parser.add_argument(
        '--config-file',
        default='archive_downloader.config',
        help='Name of the config file to create or edit',
    )
    config_parser.add_argument(
        '--default-download',
        action='store_true',
        help='Mark every file as selected when generating the config file',
    )
    config_parser.add_argument(
        '--extension',
        action='append',
        default=[],
        help='Mark one or more extensions for download after generating the config file',
    )
    config_parser.add_argument(
        '--exclude-extension',
        action='append',
        default=[],
        help='Mark one or more extensions as not selected in the config file',
    )

    download_parser = subparsers.add_parser('download', help='Download files from an archive.org item.')
    download_parser.add_argument('url', help='archive.org /details/ or /download/ URL')
    download_parser.add_argument('save_dir', help='Directory where files should be downloaded')
    download_parser.add_argument(
        '--config-file',
        help='Use an existing config file to decide which files to download',
    )
    download_parser.add_argument(
        '--extension',
        action='append',
        default=[],
        help='Download only the listed extensions, for example --extension jpg --extension xml',
    )
    download_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Use wget non-verbose mode',
    )

    return parser


def run_cli(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == 'list':
        downloader = ArchiveDownloader(args.url, args.save_dir)
        for index, filename in enumerate(downloader.list_files(), start=1):
            print(f'{index}. {filename}')
        return 0

    if shutil.which('curl') is None:
        print('curl is required and was not found on PATH.', file=sys.stderr)
        return 2

    if args.command == 'config':
        downloader = ArchiveDownloader(args.url, args.save_dir)
        downloader.generate_config_file(
            default_download=args.default_download,
            filename=args.config_file,
        )
        for extension in args.extension:
            downloader.edit_config_file(
                'extension',
                extension.lstrip('.'),
                set_download=True,
                filename=args.config_file,
            )
        for extension in args.exclude_extension:
            downloader.edit_config_file(
                'extension',
                extension.lstrip('.'),
                set_download=False,
                filename=args.config_file,
            )
        print(f'[ArchiveDownloader] Config ready: {args.config_file}')
        return 0

    if args.command == 'download':
        downloader = ArchiveDownloader(args.url, args.save_dir, wget_verbose=not args.quiet)
        if args.extension:
            downloader.select_extensions(args.extension)
            print(f'[ArchiveDownloader] Filtered to {downloader.count} files by extension.')
        downloader.get(config_file=args.config_file)
        return 0

    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(run_cli())
