# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:31:51 2022

@author: Robert
"""
#%%
from rb_custom_logger import create_custom_logger
from scrape_studios import scrape_studios
from scrape_tags import scrape_tags
from scrape_animes import scrape_animes
from scrape_reviews import scrape_reviews
from config import sleep_min, sleep_max

DB='yourdatabasename'
#%% Main `scrape_all()` function
# If the initial scrape crashes out for some reason, use the bypasses and genre index number to restart at a reasonable point.
# Dont use animes_page unless you are just looking to finish a particular genre...
def initial_scrape_all(DB = DB, studio_bypass = False, tag_bypass = False, animes_bypass = False, animes_page = 0, anime_genre_index = 0):
    #DB = 'anime7.db'
    
    """
    initial_scrape_all(..., DB = DB, studio_bypass = False, tag_bypass = False, animes_bypass = False, animes_page = 0, anime_genre_index = 0)
    
    Calls each scraper used for the initial build of the anime database.
    
    Optional keyword arguments:
    studio_bypass: Boolean used to bypass the studio scraper.
    tag_bypass: Boolean used to bypass the tag scraper.
    anime_bypass: Boolean used to bypass the anime scraper.
    animes_page: Interger value used to restart the anime scraper on a particular page.  Only use to finish a single genre.  Stop and restart on the next genre or you will continue to restart on this page on the next genre.
    anime_genre_index: Interger value used to restart the anime scraper on a particular Genre.
    """
    
    #ALTHOUGH LOGICALLY THIS SHOULD FILE LOG DEBUG and INFO, BUT IT DOESN'T.  USE message_level 3 FOR SUPPRESSED MESSAGE, and 4 and 5 AS UNSUPRESSED ON THE LINE.
    my_custom_logger = create_custom_logger('NEWDATABASE_SECONDlongrun', clevel=4, flevel=1)

    if studio_bypass == True:
        pass
    else:
        print('Step 1: Scraping Studio Information into database')
        scrape_studios(DB)

    if tag_bypass == True:
        pass
    else:
        print('Step 2: Scraping Anime Tags into database')
        scrape_tags(DB)

    if animes_bypass == True:
        pass
    else:
        print('Step 3: Scraping anime data')
        print(f'Pausing... for sleep_min: {sleep_min} to sleep_max: {sleep_max}')
        scrape_animes(DB, animes_page, anime_genre_index, sleep_min, sleep_max)

    print('Step 4: Scraping review data')
    print(f'Pausing... for sleep_min: {sleep_min} to sleep_max: {sleep_max}')
    scrape_reviews(DB, sleep_min, sleep_max)

# Dont know what this is meant to do
# if __name__ == '__main__':
#     #Create database here
#     #DB = 'anime_emptyhelpfulness.db'
#     scrape_all()


#%%
#initial_scrape_all()