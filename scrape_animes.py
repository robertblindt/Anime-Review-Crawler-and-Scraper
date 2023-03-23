# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:16:20 2022

@author: Robert
"""
import time
from requests import get
from sql_queries import run_inserts, run_query
from rb_custom_logger import send_message_to_custom_log
from bs4 import BeautifulSoup
from useful_functions import round_up
import random

DB='some_database.db'
#%% scrape_animes
# FOR SOME REASON LOG DOESNT RECOGNIZE THE UTF-8 (ANY) ENCONDING - If you rerun the same line after the error, it runs fine.
# Shortcoming - If this fails, it needs to be totally reran.  No easy way to restart the scrape from a logged page in the list of names.
#Animes, anime_tags scraper

def scrape_animes(DB=DB, animes_page=0, anime_genre_index=0, sleep_min=9, sleep_max=18):
    
    """
    scrape_animes(DB=DB, ...,animes_page=0, anime_genre_index=0, sleep_min=9, sleep_max=18)
    
    Crawls through the genre specific anime pages to scrape and insert anime information into database.
    
    DB: Name of Database for updating (requires the '.db').
    
    Optional keyword arguments:
    animes_page: Interger value used to restart the anime scraper on a particular page.  Only use to finish a single genre.  Stop and restart on the next genre or you will continue to restart on this page on the next genre.
    anime_genre_index: Interger value used to restart the anime scraper on a particular Genre.
    sleep_min: An interger argument used to represent the minimum time in seconds for randomize the pause time before moving between pages.
    sleep_max: An interger argument used to represent the maximum time in seconds for randomize the pause time before moving between pages.
    """
    
    # Same initiation as preveious function 
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
    
    # ---- Start Scraping ----
    #Makes the initial request for the Genres page.
    url = 'https://myanimelist.net/anime.php'
    headers = {"User-Agent": "mal review scraper for research."}

    # Handle timeouts
    try:
        response = get(url, headers=headers, timeout = 10)
    except:
        print('Request timeout')

    #Create the soup object to calculate the number of tags (genres)
    html_soup_initial = BeautifulSoup(response.text, 'html.parser')
    
    # Compile list of main Genres to scrape
    tag_containers = html_soup_initial.find_all('div', class_ = 'genre-link')
    tag_holder = [container.find_all('a', class_='genre-name-link') for container in tag_containers]
    # I only care about Genres right now, not themes.  In future make themes a seperate table like the tags.  Turn Tags into Genres and the new one Themes.
    alltags = tag_holder[0]+tag_holder[1]#+tag_holder[2]#+tag_holder[3]
    total_tags = len(alltags)
    
    print(f'Total Number of "genre-link" Tags: {total_tags}')

    message=f'There are {total_tags} generes.  The names and quanties within each are {alltags}'
    send_message_to_custom_log(message,message_level=3)

    # Caclulate the number of pages you need to scrape
    total_anime_pagespergenre = []
    for j in range(total_tags):
        total_anime_pagespergenre.append(round_up(float(alltags[j].text.split('(')[-1].replace(')','').replace(',',''))/100) )
    
    # Calculate the time you might spend scraping.
    total_anime_pages = sum(total_anime_pagespergenre)
    worst_case_anime_scrape = total_anime_pages*sleep_max
    best_case_anime_scrape = total_anime_pages*sleep_min
    
    message=f'There are "{total_anime_pages}" pages of animes to scrape!'
    send_message_to_custom_log(message,message_level=5)
    
    print(f'Your worst case scrape time for the Anime list is {worst_case_anime_scrape} seconds')
    print(f'That is the same thing as {worst_case_anime_scrape/60} minutes or {worst_case_anime_scrape/60/60} hours!')
    print(f'Your best case scrape time for the Anime list is {best_case_anime_scrape} seconds')
    print(f'That is the same thing as {best_case_anime_scrape/60} minutes or {best_case_anime_scrape/60/60} hours!')
    print('Both of these estimations are longer than they practically could be.  There is no way to calculate the ammount of time not spent rescraping individual Animes in multiple genres.')

    requests=0
    #Loop to obtain the name of each genre (used in html) and total number of animes in each genre (used for total page to scrape per genere)
    for j in range(anime_genre_index, total_tags):
        link_value = html_soup_initial.find_all('a', class_='genre-name-link')[j]['href']  
        #total_animes = int(html_soup_initial.find_all('a', class_='genre-name-link')[j].text.split('(')[-1].replace(')','').replace(',',''))
        
        message=f'Anime Genre Index = {j}!  This is used to manually restart after a failure.'
        send_message_to_custom_log(message,message_level=4)
        
        genre_anime_pages = int(round_up(float(alltags[j].text.split('(')[-1].replace(')','').replace(',',''))/100))
        #Loop to access each genere based anime page
        for i in range(animes_page, genre_anime_pages):

            url = 'https://myanimelist.net{0}?page={1}'.format(link_value,i+1)
            headers = {"User-Agent": "mal review scraper for research."}
            print('Scraping: {}'.format(url))

            send_message_to_custom_log(message,message_level=4)

            #Handle timeouts
            try:
                response = get(url, headers=headers, timeout = 10)
            except:
                print('Request timeout')
                pass

            #Creates the soup object
            html_soup = BeautifulSoup(response.text, 'html.parser')
            containers = html_soup.find_all('div', class_='seasonal-anime')
            
            #Parse through each page to acess and scrape and insert each anime from the page
            for container in containers:

                #Primary key for 'animes'
                anime_id = container.find('div', class_='genres js-genre').attrs['id']
                
                # Queery the database for overlapping anime_id's and skip pasing the remainder of the container if we already have it.
                q = '''
                SELECT * FROM animes
                '''
                
                table = run_query(DB, q)
                
                #If the anime has already been scraped, do not bother parsing anything else
                if int(anime_id) in table.iloc[:,0].tolist():
                    print(f'Skipping anime {anime_id} because it is already in the database!')
                    pass
                
                else: 
                #Foreign key for 'animes', use 9999 for unknown studios
                    try:
                        studio_id = int(str(containers[0].find(class_='properties')\
                                            .find_all(class_='item')[0].find('a')).split('/')[3])
                    except:
                        studio_id = 9999
    
                    #Anime info
                    anime_name = container.find(class_='h2_anime_title').text
                    episodes_total = container.find(class_='info').find_all('span')[3].text.split()[0] 
                    source_material = container.find_all(class_='property')[1].find(class_='item').text
                    air_date = container.find(class_='info').find_all('span')[0].text.split(', ')[1]
                    members = container.find(class_='member').text.strip().replace(',', '').replace('.','').replace('K','000').replace('M','000000')
                    synopsis = container.find(class_='preline').text.strip().replace('\n', '').replace('\r', '')
                    
                    try:
                        overall_rating = container.find(class_='score').text.strip()
                    except:
                        overall_rating = 'null'
    
                    #Write into SQL database, table: animes
                    try:
                        run_inserts(DB,
                            insert_query1,(
                                int(anime_id), int(studio_id), anime_name, episodes_total, source_material, \
                                air_date, overall_rating, \
                                int(members), synopsis
                            )
                        )
                        message=f'An anime with anime_id "{anime_id}" has sucessfully been added to your database!'
                        send_message_to_custom_log(message,message_level=2)
                    except Exception as e:
                        message=f'anime_id "{anime_id}" has faild to be added to your database! Error : {e}'
                        send_message_to_custom_log(message,message_level=5)
                        pass
    
                    #Container for anime_tags
                    anime_tags = [indtag for indtag in container.find('div', class_="genres-inner").find_all('a')]
                    
                    #Write into SQL database, table: animes
                    for tag in anime_tags:
                        tag_id = int(str(tag).split('/')[3])
                        try:
                            run_inserts(DB,
                                insert_query2,(
                                    int(anime_id), int(tag_id)
                                )
                            )
                            message=f'{len(anime_tags)} tags for anime with anime_id "{anime_id}" has sucessfully be added to your database!'
                            send_message_to_custom_log(message,message_level=2)
                        except Exception as e:
                            message=f'{len(anime_tags)} tags for anime with anime_id "{anime_id}" has failed to be added to your database! Error : {e}'
                            send_message_to_custom_log(message,message_level=4)
                            pass

            #Provide stats for monitoring
            current_time = time.time()
            elapsed_time = current_time - start_time
            requests += 1
            
            
            
            print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
            print('Elapsed Time: {} minutes'.format(elapsed_time/60))
            sleep_delay = random.uniform(sleep_min, sleep_max)
            print(f'Pausing for scraper delay of {sleep_delay} seconds...')
            time.sleep(sleep_delay)
    print('Scrape Complete')
    message='Anime Scrape Complete!'
    send_message_to_custom_log(message,message_level=5)

