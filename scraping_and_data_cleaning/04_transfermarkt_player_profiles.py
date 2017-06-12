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
            links.append(base_url + link.attrs['href'] + '/plus/1')
    return list(set(links))

# set download path
download_path = set_download_path('/Users/matthewmurray/ds/metis/metisgh/luther_scraping/transfermarkt/pages/squad_lists')

# set up browser
chrome_driver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chrome_driver
driver = webdriver.Chrome(chrome_driver)

years_list = [y for y in range(1999, 2017)]
# navigate to website
for y in years_list:
    url = 'http://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id={}'.format(y)
    driver.get(url)
    time.sleep(np.random.random_integers(3, 5))

    # file_string = '%s-team-info.html' % (y)
    # save_source_code(driver.page_source, download_path, file_string)

    # collect links
    bs = BeautifulSoup(driver.page_source, "lxml")
    relative_links = find_hrefs_by_regex(bs, "kader/verein")
    absolute_urls = create_absolute_urls('http://www.transfermarkt.com', relative_links)

    for url in absolute_urls:
        driver.get(url)
        time.sleep(np.random.random_integers(3, 5))
        # print(url)
        string1 = url.split('kader')[0]
        string1 = string1.replace('http://www.transfermarkt.com/', '')
        string1 = string1.replace('/','')
        team_name = string1
        file_string = '%s-%s.html' % (y, team_name)
        print(file_string)
        save_source_code(driver.page_source, download_path, file_string)

# shut down browser
driver.quit()
