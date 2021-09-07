import os
import sys
import requests
import bs4
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
        download_href_list = list(filter(lambda h: h[0] != '#', download_href_list)) # Remove page href
        download_href_list = list(filter(lambda h: h[0] != '/' and
                                 h[0:8] != 'https://', download_href_list))  # Remove archive.org href
        download_href_list = list(filter(lambda h: '.' in h, download_href_list)) # only grab files with . extension

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


    def get(self):
        '''
        Download the files from the list using wget. Let wget to handle all the incomplete files
        with the -continue and -N flag.
        '''
        os.chdir(self.save_dir)

        print(f'Downloading {self.count} files from {self.download_url} ...')

        for ind, file in enumerate(self.download_link_list):
            file_full_link = self.download_url +'/'+ file

            if self.wget_verbose == 1:
                os.system(f'wget -c -N -p {self.save_dir} --no-directories {file_full_link}')  # Continue & Timestampping
            else:
                os.system(f'wget -nv -c -N -p {self.save_dir} --no-directories {file_full_link}')

        check_set = self.compare_save_list_download_list()

        if len(check_set) == 0:
            print('\n')
            print(f'All {self.count} files downloaded from {self.download_url}.\n')
        else:
            check_str = ', '.join(list(check_set))
            print(f"Files still missing: {check_str}")



# Start of the program
if __name__ == '__main__':

    test_url = 'https://archive.org/details/KSC-KSC-69P-168'  # A photo of the S-1C booster for the Apollo 11 Saturn V rocket
    save_dir = '~/Desktop/download_test'     # Support tilde

    testdownload = ArchiveDownloader(test_url, save_dir)
    testdownload.get()

    # import pdb; pdb.set_trace()

