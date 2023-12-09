# library imports
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import argparse

def getdata(url):
    """
    Function to get html data of a website

    Args:
        url (str): website link

    Returns:
        str: html data
    """

    # add header to prevent being blocked (403 error) by wordpress websites
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    r = requests.get(url, headers=headers)
    return r.text

def get_links(website_link, website):
    """
    Function to get all links of a website

    Args:
        website_link (str): website link
        website (str): website link

    Returns:
        dict: dictionary of links
    """
    
    # get html data
    html_data = getdata(website_link)

    try:
        # parse html data
        soup = BeautifulSoup(html_data, "html.parser")
        list_links = []

        # loop through all links
        for link in soup.find_all("a", href=True):
            # append to list if new link contains original link
            if str(link["href"]).startswith((str(website))):
                list_links.append(link["href"])

            # include all href that do not start with website link but with "/"
            if str(link["href"]).startswith("/"):
                if link["href"] not in dict_href_links:
                    print(link["href"])
                    dict_href_links[link["href"]] = None
                    link_with_www = website + "/"+ link["href"][1:]
                    print("adjusted link =", link_with_www)
                    list_links.append(link_with_www)
    except:
        list_links = []
        pass
    
    # convert list of links to dictionary and define keys as the links and the values as "Not-checked"
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links

def get_subpage_links(l, website):
    """
    Function to get all links of subpages of a website

    Args:
        l (dict): dictionary of links
        website (str): website link

    Returns:
        dict: updated dictionary of links
    """

    # loop through all links
    for link in tqdm(l):

        # check if link is already crawled
        if l[link] == "Not-checked":
            # get all links of subpage
            dict_links_subpages = get_links(link, website)
            # update the dictionary value of the link to "Checked"
            l[link] = "Checked"
        else:
            # create an empty dictionary in case every link is checked
            dict_links_subpages = {}
        
        # add new dictionary to old dictionary
        l = {**dict_links_subpages, **l}
    return l

def get_subpages(link, file_name):
    """
    Function to get all subpages of a website

    Args:
        link (str): website link

    Returns:
        None
    """
    # get website link
    website = link

    # create dictionary of website
    dict_links = {website:"Not-checked"}

    # initialize counters
    counter, counter2 = None, 0

    # loop until all links are checked
    while counter != 0:
        counter2 += 1

        # get links of all subpages
        dict_links2 = get_subpage_links(dict_links, website)
        
        # count number of links that are not checked
        counter = sum(value == "Not-checked" for value in dict_links2.values())

        # print information
        print("")
        print("THIS IS LOOP ITERATION NUMBER", counter2)
        print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
        print("NUMBER OF 'Not-checked' LINKS = ", counter)
        print("")
        dict_links = dict_links2

        # save the links in json file
        a_file = open(file_name, "w")
        json.dump(dict_links, a_file)
        a_file.close()

if __name__ == "__main__":
    # create parser
    parser = argparse.ArgumentParser(
                    prog='get_subpages',
                    description='This script gets all subpages of a website and saves them in a json file.')
    parser.add_argument('website_link', type=str, help='Website link')
    parser.add_argument('file_name', type=str, help='File name')

    # parse arguments
    args = parser.parse_args()
    website_link = args.website_link
    file_name = args.file_name

    # initialize dictionary
    dict_href_links = {}

    # call function to get all subpages
    get_subpages(website_link, file_name)