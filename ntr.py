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


def download_collection(scraper, collection, chunk_size=30):
    os.makedirs(f'./images/{collection}/json_data', exist_ok=True)
    collection_data = scraper.get(f"http://api.opensea.io/api/v1/collection/{collection}?format=json")
    collection_info = json.loads(collection_data.content.decode())
    count = int(collection_info['collection']['stats']['count'])
    total_nfts = range(count)
    nft_chunks = [total_nfts[i: i + chunk_size] for i in range(0, len(total_nfts), chunk_size)]
    print(f'Beginning download of \"{collection}\" collection.')
    with tqdm(total=count) as progressbar:
        for chunk in nft_chunks:
            token_ids = (s:='&token_ids=') + s.join([str(x) for x in chunk])
            data = json.loads(scraper.get(f'https://api.opensea.io/api/v1/assets?order_direction=asc{token_ids}&limit=50&collection={collection}&format=json').text)
            if 'assets' in data:
                for asset in data['assets']:
                    id = str(asset['token_id'])
                    formatted_id = id.zfill(len(str(count)))
                    if os.path.exists(f'./images/{collection}/json_data/{formatted_id}.json'):
                        continue
                    else:
                        with open(f'./images/{collection}/json_data/{formatted_id}.json', 'w+') as f:
                            json.dump(asset, f, indent=3)
                    if os.path.exists(f'./images/{collection}/{formatted_id}.png'):
                        continue
                    else:
                        if not asset['image_url'] is None:
                            image = scraper.get(asset['image_url'])
                            if image.status_code == 200:
                                with open(f'./images/{collection}/{formatted_id}.png', 'wb+') as f:
                                    f.write(image.content)
                    progressbar.update()


if __name__ == '__main__':
    scraper = init_scraper()
    edges = parse_ranking_html(scraper, 'https://opensea.io/rankings?sortBy=')
    collection_names = get_collection_names(edges)
