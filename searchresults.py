from selectorlib import Extractor
import requests 
import pandas as pd

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('search_results_page.yml')

# Scraping function
def scrape(url):  

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': '"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.zooplus.de/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8;de-DE',
    }

    # Download the page using requests
    print("Downloading %s"%url)
    r = requests.get(url, headers=headers)

    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create 
    return e.extract(r.text)


articles = []
with open("search_results_urls.txt",'r') as urllist:
    for url in urllist.read().splitlines():
        # Pagination
        pagination = 5
        for i in range(1,pagination+1):
            urlPagination = url + '?page={}'.format(i)
            data = scrape(urlPagination)
            if data:
                # Articles
                for article in data['articles']:
                    try:
                        article['url'] = 'https://www.zooplus.de' + article['url']
                        if article['rating_score'] == None:
                            article['rating_score'] = 5
                        else:
                            article['rating_score'] = 5 - article['rating_score']
                    except:
                        pass

                # Categories
                categories = list({frozenset(item.items()): item for item in data['categories']}.values())
                categories = [d['category'] for d in categories]

            articles.extend(data['articles'])

        df_Articles = pd.DataFrame(articles)
        df_Categories = pd.DataFrame(categories)

    df_Articles.to_csv(('df_Articles.csv'))
    df_Categories.to_csv(('df_Categories.csv'))