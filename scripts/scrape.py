# library imports
from bs4 import BeautifulSoup
import requests
import html2text
import json
from tqdm import tqdm
import os
import argparse

def scrape_subdomain(json_file_name, directory):
    """
    This function scrapes all subpages of a website and saves them as text files.

    Args:
        json_file_name (str): Path to json file containing all subpages of a website.
        directory (str): Path to directory where the text files should be saved.
    
    Returns:
        None
    """

    # get the urls of all subpages
    url_list = [i for i in json.load(open(json_file_name)).keys()]    

    # initialize html2text
    h = html2text.HTML2Text()
    h.wrap_list_items = True
    h.ignore_images = True
    h.ignore_links = True
    h.ignore_tables = True

    # loop through all urls
    for i in tqdm(url_list):

        # get html data
        session = requests.session()
        req = session.get(i)
        doc = BeautifulSoup(req.content)
        
        # get the file name
        file_name = directory + "/" + i.replace('https://', '') + '.txt'
        print(file_name)
        
        # create directory if it doesn't exist
        try:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
        except:
            pass

        # write the file
        try:
            with open(file_name, 'w') as f:
                f.write(h.handle(str(doc)))
        except:
            pass

if __name__ == "__main__":
    # create parser
    parser = argparse.ArgumentParser(
                    prog='scrape',
                    description='This script scrapes all subpages of a website and saves them as text files.')
    parser.add_argument('json_file_name', type=str, help='Path to json file containing all subpages of a website.')
    parser.add_argument('directory', type=str, help='Path to directory where the text files should be saved.')

    # parse arguments
    args = parser.parse_args()
    json_file_name = args.json_file_name
    directory = args.directory

    # call function to start scraping
    scrape_subdomain(json_file_name, directory)