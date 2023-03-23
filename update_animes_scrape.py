# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:27:12 2022

@author: Robert
"""
#%%
import time
import random
from requests import get
from bs4 import BeautifulSoup
from sql_queries import run_inserts, run_query
from useful_functions import round_up
from rb_custom_logger import send_message_to_custom_log

DB=''
#%% update_animes_scrape
#How to figure out how many animes need to be scraped
#The entirety of the first anime scraper must have been run sucessfully before this works properly
#The large scale anime scrape goes by genre and not by anime ID numbers.  THIS IS BY ANIME ID
#This update scrape will be very slow as from the "Just Added" page, you will need to open each individual anime page.


def update_animes_scrape(DB=DB, sleep_min=9, sleep_max=18):
    
    """
    update_animes_scrape(..., DB, sleep_min=9, sleep_max=18)
    
    Crawls through the "just added" animes pages to scrape and insert anime information into database.
    
    Optional keyword arguments:
    DB: Name of Database for updating (requires the '.db').
    sleep_min: An interger argument used to represent the minimum time in seconds for randomize the pause time before moving between pages.
    sleep_max: An interger argument used to represent the maximum time in seconds for randomize the pause time before moving between pages.
    """
    
    requests=0
    
    start_time = time.time()
    
    insert_query1 = '''
    INSERT OR IGNORE INTO animes(
        anime_id,
        studio_id,
        anime_name,
        episodes_total,
        source_material,
        air_date,
        overall_rating,
        members,
        synopsis
        )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    insert_query2 = '''
    INSERT OR IGNORE INTO anime_tags( anime_id, tag_id ) VALUES (?, ?)
    '''
    
    url = 'https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show=0'
    headers = {"User-Agent": "mal review scraper for research."}
    
    # Handle timeouts
    try:
        response = get(url, headers=headers, timeout = 10)
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
    
    animes_to_scrape = newest_anime_id - most_recent_animeid_scraped
    
    message=f'The most recent anime ID in your Database is {most_recent_animeid_scraped}, and the most recently added anime ID is {newest_anime_id}'
    send_message_to_custom_log(message,message_level=5)
    
    if animes_to_scrape >= 50*450:
        print(f'Watch out! There are only 22,500 new animes stored in the "Just Added" page, and there are {animes_to_scrape} ID numbers between your data base and the most recent anime.  You may need to scrape the other way to get all the new animes.  Some IDs are skipped, so this is not certain. There is a stop in place in case you scrape your current most recently added anime.')
        print('If there are really 22,500 new animes, this will hit a 404 page and fail. On my first scrape in September 2022, there were only 22,200 Animes total.')
    else:
        print(f'There are {animes_to_scrape} ID numbers between your data base and the most recent anime.  Many ID numbers are skipped, so do not expect to see that number added to your database.  There is a stop in place for when you inevidably scrape the same Anime ID so it does not run unnessiarily.')
    
    pages_to_scrape = int(round_up(animes_to_scrape/50))
    
    #Getting the index of pages to retrieve and scrape
    for i in range(pages_to_scrape):
        #URL below is for the "just added" animes page.  "&show={}" is used for page indexing where pg 1 is 0, pg 2 is 50...
        url = 'https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show={}'.format((i)*50)
        
        # TODO : ADD A REAL USER AGENT
        headers = {"User-Agent": "mal review scraper for research."}
        print('Scraping URLs to Scrape: {}'.format(url))
        
        try:
            response = get(url, headers=headers, timeout = 10)
        except:
            print('Request timeout')
            
        html_soup_initial = BeautifulSoup(response.text, 'html.parser')
        anime_links=html_soup_initial.find_all(class_='picSurround')
        print(len(anime_links))
        
        
               
        #Anime page links are individually retrieved, parsedfor information, and inserted into DB.
        for anime_link in anime_links: 
            anime_url = anime_link.find('a').attrs['href']
            headers = {"User-Agent": "mal review scraper for research."}
            print('Scraping Anime from: {}'.format(anime_url))
            try:
                response = get(anime_url, headers=headers, timeout = 10)
            except:
                print('Request timeout')
                pass

            if response.status_code != 200:
                print('Request: {}; Status code: {}'.format(requests, response.status_code))
                pass

            html_soup_anime = BeautifulSoup(response.text, 'html.parser')
            left_pane=html_soup_anime.find(class_='leftside')
           
            #Primary key for 'animes'
            anime_id = anime_url.split('/')[4]
            
            if anime_id == most_recent_animeid_scraped:
                message='The most recent anime ID in your Database has been reached'
                send_message_to_custom_log(message,message_level=5)
                break
            else:

            #Foreign key for 'animes', use 9999 for unknown studios
                try:
                    studio_id = int(left_pane.find_all(class_='spaceit_pad')[7]\
                                        .find('a').attrs['href'].split('/')[3])
                except:
                    studio_id = 9999
    
                #Anime info
                anime_name = html_soup_anime.find(class_='h1-title').text
                synopsis = html_soup_anime.find(class_='rightside').find('p').text.strip().replace('\n', '').replace('\r', '')
                
                # row=left_pane.find_all(class_='spaceit_pad')[4]
                # WRITE A LOOP THAT GOES THROUGH ALL THE 'spceit_pad' and set up if elif for each parameter I want!
                # Use a selenium scroll function to make sure items are in view.
                # TODO : Is visiable! Look above. Look into the 'is visiable' command in Selenium
                for row in left_pane.find_all(class_='spaceit_pad'):
                    if row.text.split(':')[0].replace('\n','') == 'Episodes':
                        episodes_total = row.text.replace('Episodes:','').replace(' ','').replace('\n','')
                        
                    elif row.text.split(':')[0].replace('\n','') == 'Source':
                        source_material = row.text.replace('Source:','').replace(' ','').replace('\n','')
                        
                    elif row.text.split(':')[0].replace('\n','') == 'Members':
                        members = row.text.replace('Members:','').replace(' ','').replace('\n','').replace(',','').replace('K','000').replace('M','000000')
                     
                    elif row.text.split(':')[0].replace('\n','') == 'Genres':
                        anime_tags = []
                        for indtag in row.find_all('a'):
                            anime_tags.append(indtag.attrs['href'].split('/')[-2]) 
                        
                    elif row.text.split(':')[0].replace('\n','') == 'Aired':  
                        airdblock = row.text.replace('Aired:','').replace(' ','').replace('\n','').split(',')
                        if len(airdblock) >= 2:
                            try:
                                int(airdblock[1][:4])
                                air_date = airdblock[1][:4]
                            except:
                                air_date = '-'
                        elif len(airdblock[0]) >= 4:
                            air_date = airdblock[0][:4]
                            try:
                                int(air_date)
                            except:
                                air_date = '-'
                        else:
                            air_date = '-'
                    else:
                        pass  
                # TODO : Logging here to show what it was reading through.    
                
                try:
                    overall_rating = int(html_soup_anime.find(class_='score-label').text.strip())
                except:
                    overall_rating = 'null'
                #DATA COLLECTION COMPLETE FOR CURRENT ANIME PAGE.  Ready to store.
                
                #Write into SQL database, table: animes
                try:
                    run_inserts(DB,
                        insert_query1,(
                            int(anime_id), int(studio_id), anime_name, episodes_total, source_material, \
                            air_date, overall_rating, \
                            int(members), synopsis
                        )
                    )
                    message=f'{anime_id} added to the database.'
                    send_message_to_custom_log(message,message_level=3)    
                except Exception as e:
                    message=f'Failed to insert anime for anime_id: {anime_id}, {e}'
                    send_message_to_custom_log(message,message_level=5)
                    pass
    
                try:
                    #Write into SQL database, table: animes
                    for tag in anime_tags:
                        tag_id = tag
                        try:
                            run_inserts(DB,
                                insert_query2,(
                                    int(anime_id), int(tag_id)
                                )
                            )
                        except Exception as e:
                            print('Failed to insert into anime_tags for anime_id: {0}, {1}'.format(anime_id, e))
                            pass
                except:
                    message=f'THIS ANIME HAS NO TAGS!!!!! {anime_id}'
                    send_message_to_custom_log(message,message_level=5)
                    
                sleep_delay = random.uniform(sleep_min, sleep_max)
                print(f'Pausing for scraper delay of {sleep_delay} seconds...')
                time.sleep(sleep_delay)

        #Provide stats for monitoring
        current_time = time.time()
        elapsed_time = current_time - start_time
        requests += 1

        print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        print('Elapsed Time: {} minutes'.format(elapsed_time/60))
        sleep_delay = random.uniform(sleep_min, sleep_max)
        print(f'Pausing for scraper delay of {sleep_delay} seconds...')
        time.sleep(sleep_delay)
  
    