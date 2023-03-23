# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:12:46 2022

@author: Robert
"""
import time
from sql_queries import run_inserts
from rb_custom_logger import send_message_to_custom_log
import requests
from bs4 import BeautifulSoup

#%% scrape_tags
# FOR SOME REASON LOG DOESNT RECOGNIZE THE UTF-8 (ANY) ENCONDING - If you rerun the same line after the error, it runs fine.
#Tags scraper, only one page
def scrape_tags(DB):
    
    """
    scrape_tags(DB)
    
    Scrapes the anime genres page to insert Genre/Theme IDs and names into the database.
    
    DB: Name of Database for updating (requires the '.db').
    """
    
    # Same initiation as preveious function 
    start_time = time.time()

    insert_query = '''
    INSERT OR IGNORE INTO tags(
        tag_id,
        tag_name
        )
    VALUES (?, ?)
    '''

    #Makes the request
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
        
    # Compile list of Tag to be inserted into the database --- I grab the Theme Tags too because the website is not consistent in the way it displays data.
    tag_containers = html_soup.find_all('div', class_ = 'genre-link')
    tag_holder=[container.find_all('a', class_='genre-name-link') for container in tag_containers]
    alltags=tag_holder[0]+tag_holder[1]+tag_holder[2]+tag_holder[3]
    total_tags=len(alltags)

    # Loop through the List to store in the database
    for i in range(total_tags):
        result = str(alltags[i]).replace('_',' ').split('/')
        tag_id = result[3]
        tag_name = result[4].split('"')[0]
        #Write into SQL database
        try:
            run_inserts(DB, insert_query,(
                int(tag_id), tag_name)
            )
            message=f'A Tag sucessfully was inserted into your database. tag_id = {tag_id} , tag_name = {tag_name}'
            send_message_to_custom_log(message,message_level=3)
        except Exception as e:
            message=f'A Tag failed to be inserted to your database. tag_id = {tag_id} , tag_name = {tag_name}. Error : {e}'
            send_message_to_custom_log(message,message_level=4)
            pass

        print('Scraping tags data')
        print('Scraping: {}'.format(url))
        print('Inserted into database: \'{}\''.format(tag_name))

    print('Scrape Complete')
    print('Processing time: {} seconds'.format(time.time() - start_time))
    message='Tag Scrape Complete!'
    send_message_to_custom_log(message,message_level=5)

