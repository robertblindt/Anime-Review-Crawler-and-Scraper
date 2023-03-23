# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:38:24 2022

@author: Robert
"""
#%%
import requests
from bs4 import BeautifulSoup
from sql_queries import run_query
from rb_custom_logger import send_message_to_custom_log
from selenium import webdriver
from selenium.webdriver.common.by import By
from update_scrape import update_scrape

#%%

DB = 'NEWDATABASE_secondlongrun.db'
#%% Database Check

def database_update_check_and_update(DB):
    
    """
    database_update_check_and_update(..., DB)
    
    Opens each scrapers initial page to check for changes in primary key identifiers and then calls the function that calls only the scrapers that are needed to update the database.
    
    Optional keyword arguments:
    DB: Name of Database for updating (requires the '.db').
    """
    
    # Check to see if you need to add any studios to your database
    url = 'https://myanimelist.net/anime/producer'

    headers = {"User-Agent": "mal review scraper for research."}
    try:
        response = requests.get(url, headers=headers, timeout = 10)
    except:
        print('Request timeout')
    html_soup = BeautifulSoup(response.text, 'html.parser')
    total_studios = len(html_soup.find_all('a', class_ = 'genre-name-link'))
    
    q = '''
    SELECT * FROM studios
    '''
    
    table = run_query(DB, q)
    database_studio_total = len(table.iloc[:,0])-1
    if database_studio_total == total_studios:
        message='There have been no studios added since your last scrape'
        send_message_to_custom_log(message,message_level=5)
        willscrape_studios = False
    else:
        message=f'There are {total_studios-database_studio_total} Studios added to the website since your last scrape.'
        send_message_to_custom_log(message,message_level=5)
        willscrape_studios = True
     
        
     
    
    #CHECK IF NEW GENRE WAS ADDED, IF SO TELL THEM.
    q = '''
    SELECT * FROM tags
    '''
    table = run_query(DB, q)
    database_tag_total = len(table.iloc[:,0])
    url = 'https://myanimelist.net/anime.php'
    headers = {
        "User-Agent": "mal review scraper for research."
    }

    #Handle timeouts
    try:
        response = requests.get(url, headers=headers, timeout = 10)
    except:
        print('Request timeout')

    #Create the soup object
    html_soup = BeautifulSoup(response.text, 'html.parser')

    tag_containers = html_soup.find_all('div', class_ = 'genre-link')
    tag_holder=[container.find_all('a', class_='genre-name-link') for container in tag_containers]
    
    alltags=tag_holder[0]+tag_holder[1]+tag_holder[2]+tag_holder[3]
    total_tags=len(alltags)
    if database_tag_total == total_tags:
        message='There have been no tags added since your last scrape'
        send_message_to_custom_log(message,message_level=5)
        willscrape_tags = False
    else:
        print('Scraping for the info in from this page should not take any more than 5 seconds.')
        message=f'{database_tag_total-total_tags} Tags have been added to the website since your last scrape.'
        send_message_to_custom_log(message,message_level=5)
        willscrape_tags = True
    # TODO : Current method to scrape animes doesnt nessesarily grab all the animes with the new tag added to it, nor does it account for old animes with new tags added to it... Maybe not possible to grab the latter info without a super long scrape.  
    # Maybe I could write a function to look for the new genre name and then do the same crawl I did for animes for the new one.


    
    # Check out how many animes have been added since you last scraped.  
    url = 'https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show=0'
    headers = {"User-Agent": "mal review scraper for research."}
    
    # Handle timeouts
    try:
        response = requests.get(url, headers=headers, timeout = 10)
    except:
        print('Request timeout')
    
    #Create the soup object to calculate the number of tags
    html_soup_initial = BeautifulSoup(response.text, 'html.parser')
    newest_anime_id=int(html_soup_initial.find(class_='hoverinfo_trigger').attrs['href'].split('/')[4])
    #newest_anime_id
    
    q = '''
    SELECT * FROM animes
    '''
    
    table = run_query(DB, q)
    #most recent review scraped
    most_recent_animeid_scraped = table.iloc[-1,0]
    
    if newest_anime_id == most_recent_animeid_scraped:
        message='There have been no animes added since your last scrape'
        send_message_to_custom_log(message,message_level=5)
        willscrape_animes = False  
    else:
        message=f'{newest_anime_id - most_recent_animeid_scraped} animew IDs have advanced since your last scrape.  Scraping this info will take quite a while.'
        send_message_to_custom_log(message,message_level=5)
        willscrape_animes = True
        



    url = 'https://myanimelist.net/reviews.php?t=anime&p=1'
    #headers = {"User-Agent": "mal review scraper for research."}
    print('Scraping: {}'.format(url))
    driver= webdriver.Chrome(executable_path="C:\webdrivers\chromedriver.exe")
    
    driver.implicitly_wait(5)
    driver.get(url)
    
    review_containers = driver.find_elements(By.CLASS_NAME, 'review-element')
    
    #divcon is a single instance of the for loop
    divcon=review_containers[0]
    
    #Grab the main box where the main review body and lots of other usful info is held is held.
    thumbody=divcon.find_elements(By.CSS_SELECTOR,'div')[1]
    
    #Grab the reacts and review_id line
    review_id=int(thumbody.find_element(By.CLASS_NAME,'btn-reaction').get_attribute('data-id'))
    # Check the number of reviews needed
    driver.close()
    q = '''
    SELECT * FROM reviews
    '''

    table = run_query(DB, q)
    #most recent review scraped
    newest_reviewid_scraped = int(table.iloc[-1,0])
    
    if newest_reviewid_scraped == review_id:
        message='There have been no reviews added since your last scrape'
        send_message_to_custom_log(message,message_level=5)
        willscrape_reviews = False
    else:
        message=f'{review_id - newest_reviewid_scraped} anime IDs have advanced since your last scrape.  Scraping this info will take quite a while.'
        send_message_to_custom_log(message,message_level=5)
        willscrape_reviews = True
        # TODO : Need to do math to figure out how long it will take.
        

    #get the input working, and then this will do something!
    #----------------------------------- MOST IMPORTANT LINE!!!!! JUST DOESNT WORK WITHOUT THE INPUT WHILE LOOP!------------------------------
    update_scrape(DB, willscrape_studios, willscrape_tags, willscrape_animes, willscrape_reviews)

       