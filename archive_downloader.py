import os
import sys
import requests
import bs4
import pandas as pd
from urllib.parse import unquote


class ArchiveDownloader:
    '''
    ArchiveDownloader class.
    '''
    def __init__(self, input_url, save_dir, wget_verbose=True):
        '''
        Constructor. Take input URL and the directory path for saving the files
        '''
        self.download_url = ''
        self.download_link_list = []
        self.count = 0
        self.input_url = input_url
        self.save_dir = self.replace_tilde_path(save_dir)    # Replace ~ in the input path

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


    def check_download_availabilty(self):
        '''
        Check if the archive url has a download option
        '''
        if 'archive.org' not in self.input_url:
            print('Not a valid archive.org URL!')
            return False

        # If the input URL is already the download page
        if 'download' in self.input_url:
            return True

        # If it is the detail page, look for the download options and download button class
        result = requests.get(self.input_url)
        front_soup = bs4.BeautifulSoup(result.text,"lxml")
        first_test = front_soup.select('.item-download-options')
        second_test = front_soup.select('.download-button')

        return len(first_test) > 0 and len(second_test) > 0


    def get_download_list(self):
        '''
        Get a list of to-be-downloaded URLs
        '''
        dresult = requests.get(self.download_url)
        download_soup = bs4.BeautifulSoup(dresult.text,"lxml")

        download_href_list = []
        download_list = download_soup.find_all('a', href=True)

        # Clean Up the href list
        for a in download_list:
            tmp_href = a['href']
            # print("Found URL:", tmp_href)
            download_href_list.append(a['href'])

        download_href_list = list(filter(lambda h: h[-1] != '/', download_href_list))  # Remove directory href
        download_href_list = list(filter(lambda h: h[0] != '#', download_href_list))   # Remove page href
        download_href_list = list(filter(lambda h: h[0] != '/' and
                                    h[0:8] != 'https://', download_href_list))  # Remove archive.org href
        download_href_list = list(filter(lambda h: '.' in h, download_href_list)) # only grab files with .extension

        # download_href_list = list(filter(lambda h: h[0] != '%', download_href_list)) # Remove files begin with %, those could be URL encoded
        # download_href_list = [unquote(h) if h[0] == '%' else h for h in download_href_list] # If file start with %, could be URL encoded

        # Convert it to the full URL (Currently not implemented due to how check_save_dir works)
        # download_href_list = [self.download_url+'/'+h for h in download_href_list]
        return download_href_list


    def replace_tilde_path(self, in_save_dir):
        ''' Replace the ~ symbol to home '''
        return in_save_dir.replace('~', os.getenv('HOME'))


    def get_save_dir_file_list(self):
        ''' Get the file list of the save directory '''
        os.chdir(self.save_dir)
        save_dir_file_list = os.listdir()
        save_dir_file_list = list(filter(lambda h: h[0] != '.', save_dir_file_list))

        return save_dir_file_list


    def compare_save_list_download_list(self):
        ''' Compare the download_link_list with the file list in the directory '''
        in_save_list = self.get_save_dir_file_list()
        download_list_unquote = [unquote(h) for h in self.download_link_list]   # Need to unquote (decode) the URL

        return set(download_list_unquote).symmetric_difference(set(in_save_list))


    def generate_config_header(self, filename):
        ''' Write the header of the config file. Overwrite existing file '''
        with open(filename, 'w') as f:
            f.write("=" * 80+'\n')
            f.write("    ArchiveDownloader Configuration File"+'\n')
            f.write("=" * 80+'\n')


    def generate_config_file(self, default_download=False, filename='archive_downloader.config'):
        '''
        Generate a config file based on the download link list. Write the config file to the save dir.
        Also return a pd dataframe of the config file (currently removed)
        '''
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
        '''
        Read an input config file and modify the download link list and count accordingly.
        Return a boolean status flag.
        '''
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
        '''
        Edit the config file according to some criteria. Currently implemented:
        criteria=extension - select files with certain extension and set download to Y or N
        '''
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
        '''
        Download the files from the list using wget. Let wget to handle all the incomplete files
        with the -continue and -N flag.
        If config_file is provided, will only download files with download set to Y.
        '''
        os.chdir(self.save_dir)

        if config_file != None:
            if self.process_config_file(config_file):
                print(f'[ArchiveDownloader] Successfully process config file {config_file}')
            else:
                print(f'[ArchiveDownloader] Skipping config file {config_file}')


        print(f'[ArchiveDownloader] Downloading {self.count} files from {self.download_url} ...')

        for ind, file in enumerate(self.download_link_list):
            file_full_link = self.download_url +'/'+ file

            if self.wget_verbose == 1:
                os.system(f'wget -c -N -p {self.save_dir} --no-directories {file_full_link}')  # Continue & Timestampping
            else:
                os.system(f'wget -nv -c -N -p {self.save_dir} --no-directories {file_full_link}')

        check_set = self.compare_save_list_download_list()

        if len(check_set) == 0:
            print('\n')
            print(f'[ArchiveDownloader] All {self.count} files downloaded from {self.download_url}.\n')
        else:
            check_str = ', '.join(list(check_set))
            print(f"[ArchiveDownloader] Files still missing: {check_str}")



# Start of the program
if __name__ == '__main__':

    test_url = 'https://archive.org/details/KSC-KSC-69P-168'  # A photo of the S-1C booster for the Apollo 11 Saturn V rocket
    save_dir = '~/Desktop/download_test'     # Support tilde

    testdownload = ArchiveDownloader(test_url, save_dir)
    # testdownload.get()                       # Download all files

    # To download only the .jpg files
    testdownload.generate_config_file(filename='test.config')
    testdownload.edit_config_file('extension', 'jpg', set_download=True, filename='test.config')
    testdownload.get(config_file='test.config')

    # import pdb; pdb.set_trace()

