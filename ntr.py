import os
import requests
import cloudscraper
import json
from bs4 import BeautifulSoup


def init_scraper():
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }
    )
    return scraper


def parse_ranking_html(scraper, url, sort_by='one_day_volume'):
    rankings = list()
    html = scraper.get(url + sort_by).text
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup.find_all('script'):
        if 'mutant' in str(script):
            json_data = script.text
            rankings.append(json_data)
    collections = json.loads(str(rankings[-1]))
    data = collections['props']['relayCache'][0][1]['json']['data']
    edges = data['rankings']['edges']
    return edges


def get_collection_names(edges):
    collection_names = list() 
    for rank_num, edge in enumerate(edges):
        collection_names.append(edge['node']['slug'])
    return collection_names
  

if __name__ == '__main__':
    scraper = init_scraper()
    edges = parse_ranking_html(scraper, 'https://opensea.io/rankings?sortBy=')
    collection_names = get_collection_names(edges)
