'''
BeautifulSoup based script for scraping product information from
regional Craiglist websites
'''

import csv
import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

#########################################
#Trawl main page for category subpages
#########################################
def scrape_product_pages(starturl):
    #Create empty list to populate with categories
    cats = []
    req = Request(starturl, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')
    #Categories are split into 2 tables, sss0 and sss1
    table1 = soup.find(id="sss0")
    for line in table1.find_all('a', href=True):
        cats.append(line['href'])
    table2 = soup.find(id="sss1")
    for line in table2.find_all('a', href=True):
        cats.append(line['href'])
    return cats

#########################################
#Generate full URLS based on stubs returned from scrape_product_pages
#########################################
def generate_links(cats):
    urls = []
    for cat in cats:
        link = starturl + cat
        urls.append(link)
    return urls

#########################################
#Scrape each page to extract product listings
#########################################
def scrape_page(urls):
    products = []
    for url in urls:
        print('Requesting', url)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        table = soup.find(id="search-results")
        #for rows in table:
        item = table.select("li.result-row")
        for post in item:
            #Some posts eg free or biddable items do not specify a price
            try:
                price = post.select("span.result-price")[0].text
            except:
                price = '$0'
            product = post.select("a.result-title.hdrlnk")[0].text
            #Some posts eg yard sales do not have a posted date
            try:
                date_posted = post.select("time.result-date")[0].text
            except:
                date_posted = 'Today'
            #Some posts do not specify location
            try:
                loc = post.select("span.result-hood")[0].text.replace('(','').replace(')','').strip()
            except:
                loc = 'Unknown'
            post_url = post.find("a")['href']
            details = [date_posted, product, price, loc, post_url]
            products.append(details)
    #CSV file headings
    headings = ['Date', 'Product', 'Price', 'Location', 'URL']
    #Create filename
    urlsnip = re.findall('//(\S+?)[.]', starturl)[0]
    filename = urlsnip + '-craigslist.csv'
    print('Writing data to', filename)
    with open(filename, 'w') as f:
        write = csv.writer(f)
        write.writerow(headings)
        write.writerows(products)
    print('Finished')

if __name__ == "__main__":
    starturl = "https://vancouver.craigslist.org"
    scrape_page(generate_links(scrape_product_pages(starturl)))
