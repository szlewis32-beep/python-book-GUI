# Python Web Scraping GUI Project
University Programming II project to create book website GUI using Python in Visual Studio Code.


## Web Scraping File
Scraped data from [Books to Scrape](https://books.toscrape.com/)

The code:
- Prompts the user for what topic they would like to see the available books for e.g. Travel, Science Fiction, etc.
- Provides the terms of use  at x-rates.com and the information in robots.txt to verify scraping is allowed on this site.
- Returns all the books in the topic regardless of star rating or in/out of stock status. [several topics have more than one page]
- Converts pricing to US $. Uses x-rates.com for exchange rates.


## GUI Form File
This creates a GUI interace to the web-scraping routine done in the "Lewis_WebScraping.py" file.

The code:
- Allows the user to specify the site to scrape
- Uses x-rates to find exchange rates between pound and US $
- Displays topics available from the site and allows the user to select one or more topics
- For the topic selected, it displays all the book titles and their US $ cost
- Allows searching/filtering based on cost and star rating
- Allows the user to save their results to an Excel workbook file (using pandas library)


**PLEASE NOTE**:  
GUI was built on MacOS. Widgets overlap each other, so you need a high-resolution monitor to see everything on one screen. Functionality is good and works as expected.
