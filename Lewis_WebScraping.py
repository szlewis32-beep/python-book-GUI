#help from ChatGPT and Omar Abla -- assignment

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin    #allows us to concat the url's

def open_url(p):
    """
    Function to open a URL and return the response object.
    """
    response = None
    try:
        response = requests.get(p)   # request web page. Returns response object.
        response.raise_for_status()
    except requests.exceptions.HTTPError as eh:  # handles HTTP errors like 4xxx/5xxx
        print('http error', eh)
    except requests.exceptions.ConnectionError as ec:  # handles connection errors like site doesn't exist
        print('Error connecting', ec)
    except requests.exceptions.Timeout as et: # handles timeout errors
        print('Timeout Error:', et)
    except requests.exceptions.RequestException as er:  # handles other request exceptions
        print('request exception', er)

    return response   

def get_categories(base_url):   #scrapes and get the categories from the base URL

    response = open_url(base_url)
    categories = {}     #returns the categories in a dictionary
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        category_links = soup.find('div', class_='side_categories').find('ul').find_all('a')    #finds all the categories in the site 
        for link in category_links:
            category_url = link.get('href')     #gets the href link to add to the url
            category = link.text.strip()
            categories[category] = category_url
    return categories

def get_exchange_rate():        #scrapes and gets the exchange rate from x-rates.com
    url = 'https://www.x-rates.com/calculator/?from=GBP&to=USD'
    response = open_url(url)
    exchange_rate = None
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        rate_div = soup.find("span", class_="ccOutputRslt")     #finds the exact exchange rate to calculate
        if rate_div:
            rate_text = rate_div.text.strip()
            rate_numeric = ''.join(filter(lambda x: x.isdigit() or x == '.', rate_text))
            exchange_rate = float(rate_numeric)     #returns the exchange as a float
    return exchange_rate


def get_books(topic_url):
    base_url = "http://books.toscrape.com/"
    books = []

    while True:
        url = urljoin(base_url, topic_url)
        response = open_url(url)
        if not response or response.status_code != 200:
            print(f"Failed to fetch books for '{topic_url}'.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        book_divs = soup.find_all("article", class_="product_pod")

        exchange_rate = get_exchange_rate()

        if exchange_rate is None:
            print("Failed to fetch the exchange rate. Prices will be in GBP.")
            return []

        for div in book_divs:
            title = div.h3.a["title"]
            price = float(div.select_one('.price_color').get_text()[2:])
            star_rating_class = div.select_one('.star-rating')['class'][1]
            star_rating = star_rating_class.split("-")[-1]  # Extract the star rating from the class
            price_usd = price * exchange_rate
            books.append({"title": title, "price_usd": price_usd, "star_rating": star_rating})

        next_page_link = soup.select_one(".next a")
        if not next_page_link:
            break
        next_href = next_page_link.get('href')
        topic_url = urljoin(topic_url, next_href)

    return books




def main():
    """
    Main function to run the program.
    """
    base_url = "http://books.toscrape.com/"
    categories = get_categories(base_url)       #gets the categories
    print("Available categories:")
    for category in categories:
        print(category)

    while True:
        topic = input("Enter the category or genre you would like to see available books for: ").strip().title()        #user input for the category
        if topic in categories:
            books = get_books(categories[topic])
            if books:
                print(f"\nAvailable books in the '{topic}' category:")
                for book in books:
                    print(f"Title: {book['title']}, Price (USD): ${book['price_usd']:.2f}, Star Rating: {book['star_rating']}")         #print statement for book and price in usd
            else:
                print(f"No books found in the '{topic}' category.")
            break
        else:
            print("Invalid category. Please enter a valid category.")

if __name__ == "__main__":      #ensure the code runs
    main()


'''
In your script, provide the terms of use  at x-rates.com and the information in robots.txt to verify you understand if scraping is allowed on this site.

The terms of use from the website state that we can use anything from this site as long as we don't distribute it 
or transfer copies to others in exchange for money. We are also not allowed to use special software to parse content 
from the site. The robots.txt from the site also allows us to see what we are able to access. The only thing we aren't allowed 
to access was to get authorization of the site, but other than that it gave us the sitemaps that we are able to scrape.


robots.txt (below)
User-agent: *
Disallow: /auth/

# sitemap xml
Sitemap: https://www.x-rates.com/sitemap-table-1.xml
Sitemap: https://www.x-rates.com/sitemap-graph-1.xml
Sitemap: https://www.x-rates.com/sitemap-calculator-1.xml
Sitemap: https://www.x-rates.com/sitemap-monthly-average-1.xml
Sitemap: https://www.x-rates.com/sitemap-historical-1.xml
Sitemap: https://www.x-rates.com/sitemap-general.xml
'''