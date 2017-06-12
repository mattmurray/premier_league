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
download_path = set_download_path('/Users/matthewmurray/ds/metis/metisgh/luther_scraping/transfermarkt/pages')

## open each individual page

# load each saved html file and store in bs object
file_path = download_path + '/transfer_data_*'
file_list = glob.glob(file_path)

for f in file_list:
    base = os.path.basename(f)
    file_name = os.path.splitext(base)[0]
    transfer_year = file_name[-4:]

    with open(f, "r") as f:
        page = f.read()
        bs = BeautifulSoup(page, "lxml")
        bs_divs = bs.find_all('div', class_='box')
        transfer_dfs = []

        for div in bs_divs:
            if div.find('th', class_='spieler-transfer-cell') != None:

                try:
                    team_name = div.find('div', class_='table-header').text
                except AttributeError:
                    team_name = np.nan

                tables = div.find_all('table')
                df = pd.read_html(str(tables), flavor='bs4', header=0)

                # first work on transfer arrivals
                arrivals = df[0]
                # dataframe is a bit messed up..needs a bit of tidying up..

                # delete nationality, moving from and Pos columns
                arrivals = arrivals.drop(['Nat.', 'Moving from', 'Pos'], axis=1)
                # rename the transfer fee column to team_from
                arrivals = arrivals.rename(columns={'Transfer fee': 'other_team'})
                # last column name is unnamed - fix to 'transfer_fee'
                last_col_name = arrivals.columns[len(arrivals.columns) - 1]
                arrivals.rename(columns={last_col_name: 'transfer_fee'}, inplace=True)
                # add a new column to the dataframe for 'team_to'
                arrivals['team'] = team_name
                arrivals['transfer_type'] = 'In'
                # clean column names
                arrivals.rename(columns={'Arrivals': 'player_name', 'Age': 'player_age', 'Position': 'player_position',
                                         'Market value': 'current_value'}, inplace=True)
                # clean player names
                arrivals['player_name'] = arrivals['player_name'].apply(lambda s: s[0:s.find('.') - 1])
                arrivals['transfer_year'] = transfer_year
                transfer_dfs.append(arrivals)

                departures = df[1]
                # delete nationality, moving to and Pos columns
                departures = departures.drop(['Nat.', 'Moving to', 'Pos'], axis=1)
                # rename the transfer fee column to team_from
                departures = departures.rename(columns={'Transfer fee': 'other_team'})
                # last column name is unnamed - fix to 'transfer_fee'
                last_col_name = departures.columns[len(departures.columns) - 1]
                departures.rename(columns={last_col_name: 'transfer_fee'}, inplace=True)
                # add a new column to the dataframe for 'team_to'
                departures['team'] = team_name
                departures['transfer_type'] = 'Out'

                # clean column names
                departures.rename(
                    columns={'Departures': 'player_name', 'Age': 'player_age', 'Position': 'player_position',
                             'Market value': 'current_value'}, inplace=True)
                # clean player names
                departures['player_name'] = departures['player_name'].apply(lambda s: s[0:s.find('.') - 1])
                departures['transfer_year'] = transfer_year
                transfer_dfs.append(departures)

                df = pd.concat(transfer_dfs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None,
                               levels=None, names=None, verify_integrity=False, copy=True)
                download_path = set_download_path(
                    '/Users/matthewmurray/ds/metis/metisgh/luther_scraping/transfermarkt/data')
                df.to_csv(download_path + '/transfers_' + transfer_year + '.csv', index=False)

            else:
                continue