# Anime-Review-Crawler-and-Scraper
 This is a learning project intended to teach myself about general Python functions, troublshooting, and webscraping.  It updates Seng Chu's 'mal-review-scraper' project to work with the current state of the 'MyAnimeList.net'. (as of November 2022)

## **Project & Work Product Description**
- **Main Goals:** 
  - Learn Python application design, coding, and debugging tools (Spyder, Jupyter) for Data Analytics 
  - Get significant hands-on experience dissecting, debugging, updating, and refining an end-to-end webscraping application
  - Learn many popular Python packages (Beautiful Soup, Selenium, Requests, Logging, others)
- **Secondary Goals:**
  - Learn Pandas for data wrangling and SQL databases for persistent storage
  - Learn key technologies used in web application development (HTML, CSS, Javascript, Selenium Webdriver)
- **Main Deliverables:** 
  - Strong hands-on skills and knowledge used to analyze, debug, and fix code problems in existing applications
  - Working code for the updated website crawler, scraper, and database builder
  - Lessons learned about the design and maintenance of *fault-tolerant* data scraping applications
  
## Description of Solution:
This application uses both BeautifulSoup and Selenium to find and parse data, and then uses SQL to store and manage the database.  There is also a short script that employs Seaborn and Matplotlib to display data.  (That script is from the original project, but has some markups from me learning what was going on)

## Solution Design (high-level):
- **Initial Data Capture** (parse) and **Database Build and Data Storage**:
  - Capture the Studio ID Numbers and Studio Names from Studio page.
  - Capture the Genre and Theme Names and ID Numbers
  - Crawl and store the "Genre specific" Animes pages to retrieve the Anime IDs and other useful data
  - Crawl and store the user reviews pages to retrieve review content
- **Database Update** (Capture Recently Added Data):
  - Query and compare each scraper starting page ("latest") for changes to the key identifiers to decide which scrapers to invoke
    - Retrieve Studio ID Numbers and Names from Studios page; compare with database to identify new Studios
    - Retrieve the Genre and Theme Names and ID Numbers; compare with database to identify new Genres and Animes
    - Retrieve the most recent Anime ID; compare with database to identify if crawl is needed
    - Retrieve the most recent Review ID; compare with database to identify if crawl is needed
  - Call the required scrapers
  
### Solution Code Description: 
Data capture is achieved using a mix of BeautifulSoup (BS4) and Selenium.  The initial project exclusively used BS to scrape the site, but many elements on the site have moved or changed since the scraper was first completed in 2019.  Many user-related website interactions used dynamic Javascript, so the static BS4 parser could not be used.  For that reason, I integrated Selinum web automation functions to perform dynamic data requests.


### Main function Caller
- `main.py`

### Application structure and functions       
The "main()" application program uses the two following modules:
- `initial_scrape_all.py`
- `database_update_check_and_update.py`

The two main application modules call functions within these modules:
- `rb_custom_logger.py` - Custom logger used throughout to track progress and debug issues.
- `make_database.py` - Gets user input to create or select the database 
- `sql_queries.py` - Python SQL query commands to build tables, read, and insert objects into the database
- `useful_functions.py` - Utility functions (round_up(), round_down())
- `scrape_studios.py` - Scrapes and captures Studio objects into database
- `scrape_tags.py` - Scrapes and captures Tag objects (metadata for animes, genres) into database 
- `scrape_animes.py` - Scrapes and captures Anime objects into database (inital data capture)
- `scrape_reviews.py` - Scrapes and captures Review objects into the database
- `update_animes_scrape.py` - Scrapes and captures new animes to database (used after the initial pool of animes is captured)

A few basic statistics were provided in the original project that I ran to ensure that the database was properly created.  These are in `anime_stats_v0.py`.  There are not functions, but short console commands to ensure the database is functional. 


## Application Use: 
- Open 'main.py'
    - Run the imports and function definition
    - Run the line "main()"
        - It will ask you if you would like to do an intial scrape or an update.  It will also give you a quit option.  Once selected you will have to enter the name of the database you would like to create or interact with.  From there it should run completely hands off until it has completed its initial scrape.
		
		
## Installation:
    1) Create a new Environment with python 3.8 or 3.9 (the two environments tested in)
    2) Install Spyder and any other programs you like to have in your environment (jupyter, command line utilities, etc)
    3) pip install pandas
    4) pip install selenium
    5) From here, use the steps in "Application Use" to run the scrapers