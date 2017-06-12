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
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0

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

## navigate to wikipedia to get urls to all the old premier league tables back to 1992

# set download path
download_path = set_download_path('/Users/matthewmurray/ds/metis/metisgh/luther_scraping/wikipedia/pages')

# set up browser
chrome_driver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chrome_driver
driver = webdriver.Chrome(chrome_driver)

# navigate to website
driver.get("https://en.wikipedia.org/wiki/List_of_Premier_League_seasons")

# save html to file
save_source_code(driver.page_source, download_path, 'base_wiki.html')

# shut down browser
driver.quit()

# ------------------------------------

## Open saved file, collect next set of links and download pages

# load saved html file and store in bs object
url = download_path + '/base_wiki.html'
with open(url, "r") as f:
    page = f.read()
tree = html.fromstring(page)
html = lxml.html.tostring(tree)
bs = BeautifulSoup(html, "lxml")

# drill down to table of premier league seasons
bs_table = bs.find('table', {'id': 'collapsibleTable0'})

#collect all links
relative_links = find_hrefs_by_regex(bs_table, "/wiki/\d")
titles_urls_dict = {link.text: 'https://en.wikipedia.org' + link.attrs['href'] for link in relative_links}

# download all individual wiki pages
driver = webdriver.Chrome(chrome_driver)
counter = 0
for k, v in titles_urls_dict.items():
    driver.get(v)
    save_source_code(driver.page_source, download_path, 'table-' + str(k) + '.html')
    counter += 1
    time.sleep(np.random.random_integers(1, 5))

# shut down browser
driver.quit()

# ------------------------------------

## open each individual page and download the league tables from them

# load each saved html file and store in bs object
file_path = download_path + '/table-*'
file_list = glob.glob(file_path)

for file_item in file_list:
    # print(f)
    base = os.path.basename(file_item)
    # print(base)
    file_name = os.path.splitext(base)[0]
    # print(file_name)
    with open(file_item, "r") as f:
        page = f.read()
        bs = BeautifulSoup(page, "lxml")

        # drill down to league table, export to dataframe and save to csv
        league_table_heading = bs.find('span', id=re.compile('eague_table'))
        league_table = league_table_heading.find_next('table')

        df = pd.read_html(str(league_table), flavor='bs4', header=0)
        df = df[0]

        download_path = set_download_path('/Users/matthewmurray/ds/metis/metisgh/luther_scraping/wikipedia/data')
        df.to_csv(download_path + '/' + file_name + '.csv')