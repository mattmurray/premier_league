import os
import glob
import numpy as np
from bs4 import BeautifulSoup
from lxml import html
import lxml
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0


def set_download_path(my_path):
    download_path = my_path
    if not os.path.exists(download_path):
        os.makedirs(download_path, exist_ok=True)
    return download_path


def save_source_code(html_source, path, filename):
    source_code = html_source
    f = open(path + '/' + filename, 'wb')
    f.write(source_code.encode('utf-8'))
    f.close()


def find_hrefs_by_regex(bs, reg_exp):
    all_items = bs.find_all("a", href=re.compile(reg_exp))
    return all_items


def create_absolute_urls(base_url, rel_links):
    links = []
    for link in rel_links:
        if 'href' in link.attrs:
            links.append(base_url + link.attrs['href'])
    return list(set(links))

# set download path
download_path = set_download_path('/Users/matthewmurray/ds/metis/metisgh/luther_scraping/transfermarkt/pages/team_info')

# load each saved html file and store in bs object
file_path = download_path + '/*team-info.html'
file_list = glob.glob(file_path)

test_file = file_list[0]
base = os.path.basename(test_file)
file_name = os.path.splitext(base)[0]

with open(test_file, "r") as f:
    page = f.read()
    bs = BeautifulSoup(page, "lxml")
    bs_tables = bs.find('table', class_='items')
    df = pd.read_html(str(bs_tables))
    print(df)

# for f in file_list:
#     base = os.path.basename(f)
#     file_name = os.path.splitext(base)[0]
#     transfer_year = file_name[-4:]
#
#     with open(f, "r") as f:
#         page = f.read()
#         bs = BeautifulSoup(page, "lxml")
#         bs_divs = bs.find_all('div', class_='box')
#         transfer_dfs = []