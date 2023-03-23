# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:09:43 2022

@author: Robert
"""
#%%
import time
from sql_queries import run_command, run_inserts
from rb_custom_logger import send_message_to_custom_log
import requests
from bs4 import BeautifulSoup

#%% scrape_studios
# FOR SOME REASON LOG DOESNT RECOGNIZE THE UTF-8 (ANY) ENCONDING - If you rerun the same line after the error, it runs fine.
# Studios scraper, only one page
def scrape_studios(DB):
    
    """
    scrape_studios(DB)
    
    Scrapes the producers/studios page to insert studio ID and names into database.
    
    DB: Name of Database for updating (requires the '.db').
    """

    # Get current time for scraper duration calculations.
    start_time = time.time()

    insert_query = '''
    INSERT OR IGNORE INTO studios(
        studio_id,
        studio_name
        )
    VALUES (?, ?)
    '''

    # Create a special entry 'studio_id=9999' for unknown studios
    insert_special = '''
    INSERT OR IGNORE INTO studios(
        studio_id,
        studio_name
        )
    VALUES (9999, 'Unknown')
    '''

    # Insert a single record for unknown studios
    run_command(DB, insert_special)
    
    #get a randomlized user agent
    # ua = shadow_useragent.ShadowUserAgent()
    # uas = ua.get_uas()
    
    
    # URL to Master Studio Index Page to Request the List of All Studios
    # TODO : USE A REAL USER AGENT
    url = 'https://myanimelist.net/anime/producer'
    headers = {"User-Agent": "mal review scraper for research."}

    # Handle timeouts
    try:
        response = requests.get(url, headers=headers, timeout = 10)
    except:
        print('Request timeout')

    # Creates the soup object
    html_soup = BeautifulSoup(response.text, 'html.parser')
    
    # Grab the quantity of studios so you can index through the links
    total_studios = len(html_soup.find_all('a', class_ = 'genre-name-link'))

    # Loop through each studio name to get the name and ID number
    for i in range(total_studios):
        result = html_soup.find_all('a', class_ = 'genre-name-link')[i].attrs['href'].replace('/anime/producer/', '').split('/', 1)
        studio_id = result[0]
        studio_name = result[1]

        #Write into SQL database
        try:
            run_inserts(DB, insert_query,(
                int(studio_id), studio_name)
            )
            send_message_to_custom_log(f'The studio {studio_name} {studio_id} was sucessfully added to your database', message_level = 3)
            
        except Exception as e:
            send_message_to_custom_log(f'The studio {studio_name} {studio_id} has failed to be added to your database. {e}', message_level = 4)
            pass

        # Provide statistics for monitoring
        print('Scraping studio data')
        print('Scraping: {}'.format(url))
        print('Inserted into database: \'{}\''.format(studio_name))

    message=f'{scrape_studios.__name__} finished in Processing time: {time.time() - start_time} seconds'
    send_message_to_custom_log(message,message_level=5)
    
    #Thinking about playing with a function to auto create messages?
    message='Studio Scrape Complete!'
    send_message_to_custom_log(message,message_level=5)

