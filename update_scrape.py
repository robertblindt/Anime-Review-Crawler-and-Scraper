# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:35:25 2022

@author: Robert
"""
#%% 
from rb_custom_logger import create_custom_logger
from scrape_studios import scrape_studios
from scrape_tags import scrape_tags
from update_animes_scrape import update_animes_scrape
from scrape_reviews import scrape_reviews
from config import sleep_min, sleep_max

#%% Update Scrape
def update_scrape(DB, willscrape_studios, willscrape_tags, willscrape_animes, willscrape_reviews):
    
    """
    update_scrape(DB, willscrape_studios, willscrape_tags, willscrape_animes, willscrape_reviews)
    
    Calls each scraper needed to update the database.
    
    DB: Name of Database for updating (requires the '.db').
    willscrape_studios: Boolean used to bypass the studio scraper.
    willscrape_tags: Boolean used to bypass the tag scraper.
    willscrape_animes: Boolean used to bypass the animes scraper.
    willscrape_review: Boolean used to bypass the review scraper.
    """
    
    my_custom_logger = create_custom_logger('NEWDATABASE_SECONDlongrun', clevel=4, flevel=1)
    
    if willscrape_studios == True:
        print('Scraping Studio Information into database')
        scrape_studios(DB)
    else:
        pass
    
    if willscrape_tags == True:
        print('Scraping Anime Tags into database')
        scrape_tags(DB)
    else:
        pass
    
    if willscrape_animes == True:
        print('Scraping anime data')
        print(f'Pausing... for sleep_min: {sleep_min} to sleep_max: {sleep_max}')
        update_animes_scrape(DB, sleep_min, sleep_max)
    else:
        pass
    
    if willscrape_reviews == True:
        print('Scraping review data')
        print(f'Pausing... for sleep_min: {sleep_min} to sleep_max: {sleep_max}')
        scrape_reviews(DB, sleep_min, sleep_max)
    else:
        pass
