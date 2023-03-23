# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:43:58 2022

@author: Robert
"""

#%%  Main module
"""
Instructions:

    1) Create the database using the script named:  "MAL-database-interface.py"

    2) Call the scraper functions in this order:

        A: scrape_studios(DB): Studio data into DB using function:
        B: scrape_tags(DB):    Anime Tags into DB using function:
        C: scrape_animes(DB, sleep_min, sleep_max): Anime data into DB:
        D: Review data into DB using function:

    The system will insert random delays in between scraping rounds to not overload the server.

"""

#%%  Import Required Packges

import sqlite3
import requests
from requests import get
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from rb_custom_logger import create_custom_logger, send_message_to_custom_log
#import shadow_useragent 

from config import sleep_min, sleep_max#, page_start, page_end

#%% Define the Name of the Database to Create

DB = 'NEWDATABASE_secondlongrun.db'

####################################################################################
#Make a master log file, and then log into it.  YOU CAN NOT HAVE MORE THAN ONE basicConfig LOGGER RUNNING AT ANY GIVEN TIME!

#%% PRODUCTION Interface for SQLite database ==> USED AFTER THE DATABASE IS CREATED

def run_query(DB, q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)

def run_command(DB, c):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c)

# PRAGMA foreign_keys = OFF seems to be the wrong choice for enforcing foreign_key contraints, but there is an
# inexplicable failure on entire pages for seemingly no good reason in the "anime_scrape" scripts. 
def run_inserts(DB, c, values):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = OFF;')
        conn.isolation_level = None
        conn.execute(c, values)

#Needed for the estimations!
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


#%%
def make_database():
    DB = input('What is the name of the Database you would like to create/update?\n')
    if DB[:-3] != '.db':
        DB = DB+'.db'
    else:
        pass
    
    try:
        #Create the reviews table
        c1 = """
        CREATE TABLE reviews(
            review_id INTEGER PRIMARY KEY,
            anime_id INTEGER,
            anime_name TEXT,
            username TEXT,
            review_date TEXT,
            overall_rating INT,
            total_helpful_counts INT,
            review_body TEXT,
            FOREIGN KEY(anime_id) REFERENCES animes(anime_id)
        );
        """
    
        run_command(DB,c1)
    
        #Create the animes table
        c2 = """
        CREATE TABLE animes(
            anime_id INTEGER PRIMARY KEY,
            anime_name TEXT,
            studio_id INT,
            episodes_total TEXT,
            source_material TEXT,
            air_date TEXT,
            overall_rating FLOAT,
            members INT,
            synopsis TEXT,
            FOREIGN KEY(studio_id) REFERENCES studios(studio_id)
        );
        """

        run_command(DB,c2)
        
        #Create the tags table
        c3 = """
        CREATE TABLE tags(
            tag_id INTEGER PRIMARY KEY,
            tag_name TEXT
        );
        """

        run_command(DB,c3)
        
        #Create the anime_tags table
        c4 = """
        CREATE TABLE anime_tags(
            anime_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY(anime_id, tag_id)
            FOREIGN KEY(anime_id) REFERENCES animes(anime_id),
            FOREIGN KEY(tag_id) REFERENCES tags(tag_id)
        );
        """

        run_command(DB,c4)
        
        #Create the studios table
        c5 = """
        CREATE TABLE studios(
            studio_id INTEGER PRIMARY KEY,
            studio_name TEXT
        );
        """

        run_command(DB,c5)
        
        send_message_to_custom_log(f'Database created by the name {DB}', message_level = 5)
        return DB
        
    except:
        send_message_to_custom_log(f'Database by the name {DB} already exsists!', message_level = 5)
        return DB
        
    
#%% scrape_studios
# FOR SOME REASON LOG DOESNT RECOGNIZE THE UTF-8 (ANY) ENCONDING - If you rerun the same line after the error, it runs fine.
# Studios scraper, only one page
def scrape_studios(DB):
    """
    NEED DOCSTRING HERE
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


#%% scrape_tags
# FOR SOME REASON LOG DOESNT RECOGNIZE THE UTF-8 (ANY) ENCONDING - If you rerun the same line after the error, it runs fine.
#Tags scraper, only one page
def scrape_tags(DB=DB):
    
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
        response = get(url, headers=headers, timeout = 10)
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


#%% scrape_animes
# FOR SOME REASON LOG DOESNT RECOGNIZE THE UTF-8 (ANY) ENCONDING - If you rerun the same line after the error, it runs fine.
# Shortcoming - If this fails, it needs to be totally reran.  No easy way to restart the scrape from a logged page in the list of names.
#Animes, anime_tags scraper

def scrape_animes(DB=DB, animes_page=0, anime_genre_index=0, sleep_min=9, sleep_max=18):
    
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


#%% scrape_reviews

def scrape_reviews(DB=DB, sleep_min=0, sleep_max=10):
    
    start_time = time.time()
    
    insert_query = '''
    INSERT OR IGNORE INTO reviews(
        review_id,
        anime_id,
        anime_name,
        username,
        review_date,
        overall_rating,
        total_helpful_counts,
        review_body
        )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''

    q = '''
    SELECT * FROM reviews
    '''

    """
    sleep_min=0
    sleep_max=10
    """

    #The Halloween update removed the sort functions for some odd reason...
    #The sort link below just links to the first page which is the most recent review page.
    #For some reason this update has cause a lot of the older pages to load rather slowly.
    
    # ---- ESTIMATE SCRAPE TIMES ----
    # Hopefully the sort options come back
    #url = 'https://myanimelist.net/reviews.php?t=anime&sort=newest'
    
    # Opens first page to estimate scrape time using the most recent review ID number
    url = 'https://myanimelist.net/reviews.php?t=anime&p=1'
    #headers = {"User-Agent": "mal review scraper for research."}
    print('Scraping: {}'.format(url))

    driver= webdriver.Chrome(executable_path="C:\webdrivers\chromedriver.exe")

    driver.get(url)
    
    review_containers = driver.find_elements(By.CLASS_NAME, 'review-element')
    
    #divcon is a single instance of the for loop
    divcon=review_containers[0]
    
    #Grab the main box where the main review body and lots of other usful info is held is held.
    thumbody=divcon.find_elements(By.CSS_SELECTOR,'div')[1]
    
    #Grab the reacts and review_id line
    review_id=thumbody.find_element(By.CLASS_NAME,'btn-reaction').get_attribute('data-id')
    
    #ENSURE THAT THIS IS SORTING BY MOST RECENT BEFORE RUNNING
    url = 'https://myanimelist.net/reviews.php?t=anime&p=1'
    #headers = {"User-Agent": "mal review scraper for research."}
    print('Scraping: {}'.format(url))
    #driver= webdriver.Chrome(executable_path="C:\webdrivers\chromedriver.exe")
    
    driver.implicitly_wait(5)
    driver.get(url)
    time.sleep(3)
    
    review_containers = driver.find_elements(By.CLASS_NAME, 'review-element')
    
    #divcon is a single instance of the for loop
    divcon=review_containers[0]
    
    #Grab the main box where the main review body and lots of other usful info is held is held.
    thumbody=divcon.find_elements(By.CSS_SELECTOR,'div')[1]
    
    #Grab the reacts and review_id line
    review_id=thumbody.find_element(By.CLASS_NAME,'btn-reaction').get_attribute('data-id')
    
    try:
        table = run_query(DB, q)
        #most recent review scraped
        newest_reviewid_scraped = table.iloc[-1,0]
        oldest_reviewid_scraped = table.iloc[0,0]
        number_of_reviews_scraped = len(table.iloc[:,0])
        number_of_review_ids_advanced = table.iloc[-1,0]-table.iloc[1,0]
        number_of_omitted_reviews = number_of_review_ids_advanced-number_of_reviews_scraped
        
        
        #If it sucessfully has scraped the whole data base before.
        
        ## I need to find a way to count the number of IDs in the list, take the highest and lowest number, and subtract that number of reviews to get the pages right.
        
        if oldest_reviewid_scraped == 1:
            page_start = 0
            #this might scrape an extra page or two due to reviews that have been taken down. 
            page_end = int(round_up((int(review_id)-newest_reviewid_scraped)/50))
            
        #If it crashed midway through the first time, it will give the pages remaining and not the newest ones to scrape.
        else:
            page_start = int(round_down((int(review_id) - oldest_reviewid_scraped - number_of_omitted_reviews)/50))
            #this number will always be too high due to the number of deleted reviews.  There are actually 4300ish pages as of 10/27/2022 - /2 added to make it closer
            page_end = int(round_up(int(review_id)/50/2))
    #if no reviews exsist(aka first run)
    except:
        page_start=0
        #The "/2" is because I know there are about 50% of the pages missing.
        page_end=int(round_up(int(review_id)/50/2))
    
    totalpages = page_end-page_start
    
    #driver.close()
    
    
    best_case_wait_time_review=totalpages*(sleep_min+2)
    
    worst_case_wait_time_reviews=totalpages*(sleep_max+2)
    
    print(f'Scraping reviews from page {page_start} to {page_end}')
    print('There are {totalpages} pages of Anime Reviews to scrape.')
    print(f'Your worst case scrape time for the reviews is {worst_case_wait_time_reviews} seconds')
    print(f'That is the same thing as {worst_case_wait_time_reviews/60} minutes or {worst_case_wait_time_reviews/60/60} hours!')
    print(f'Your best case scrape time for the Anime list is {best_case_wait_time_review} seconds')
    print(f'That is the same thing as {best_case_wait_time_review/60} minutes or {best_case_wait_time_review/60/60} hours!')
    print('KEEP IN MIND THAT THERE ARE ONLY ABOUT HALF AS MANY PAGES AS THIS CALCULATES!')
    
    
    #START SCRAPING
    
    #Open first page of reviews to scrap and itterate through them one by one.
    for j in range(page_start, (page_end + 1)):

        #Makes the request
        url = 'https://myanimelist.net/reviews.php?t=anime&p={}'.format(j)

        # Inform the user what page is current being scraped.
        message='Scraping: {}. THIS IS USED TO MANUALLY RESTART IN CASE OF FAIL!'.format(url)
        send_message_to_custom_log(message,message_level=5)

        #Open Desired page
        driver.implicitly_wait(30)
        driver.get(url)
        time.sleep(5)
        #Try to access the page the first time.  (504 errors have occured)
        if driver.find_element(By.CSS_SELECTOR, 'h1').get_attribute('textContent') ==  'Anime Reviews':
            review_containers = driver.find_elements(By.CLASS_NAME, 'review-element')
            
            
            #Loops through the containers on a page
            for container in review_containers:
                
                #Grab the title box for use with anime_id, anime_name, 
                titlebox=container.find_elements(By.CSS_SELECTOR,'div')[0]
                #Grab the main box where the main review body and lots of other usful info is held is held.
                thumbody=container.find_elements(By.CSS_SELECTOR,'div')[1]
                
                #Review Id (Primary Key)
                review_id = thumbody.find_element(By.CLASS_NAME, 'btn-reaction').get_attribute('data-id')
                
                
                if int(review_id) in table.iloc[:,0].tolist():
                    message='Review Scrape Complete!'
                    send_message_to_custom_log(message,message_level=5)
                    break
                
                else:
                #Anime Id (Foreign Key)
                    try:
                        anime_id = titlebox.find_element(By.CLASS_NAME, 'title').get_attribute('href').split('/')[4]
            
                        #Review info
                        anime_name = titlebox.find_element(By.CLASS_NAME, 'title').get_attribute('textContent')
                        username = thumbody.find_element(By.CLASS_NAME, 'username').get_attribute('textContent').replace('\n','').replace(' ','')
                        review_date = thumbody.find_element(By.CLASS_NAME,'update_at').get_attribute('textContent')
            
                        #Review ratings
                        overall_rating = thumbody.find_element(By.CLASS_NAME, 'num').get_attribute('textContent')
            
            
                        #Review helpful counts - I considered a helpful responce as 'nice', 'love it', and 'well-written'.
                        try:
                            nice = int(thumbody.find_element(By.CLASS_NAME, 'nice').find_element(By.CLASS_NAME, 'num').get_attribute('textContent')) 
                            if nice == None:
                                nice=0
                        except Exception as e:
                            nice = 0
                            #PUT A GOOD LOGGING STATMENT IN HERE! 
                            
                        try:
                            loveit = int(thumbody.find_element(By.CLASS_NAME, 'loveit').find_element(By.CLASS_NAME, 'num').get_attribute('textContent')) 
                            if loveit == None:
                                loveit=0
                        except Exception as e:
                            loveit = 0 
                            #PUT A GOOD LOGGING STATMENT IN HERE! 
                        
                        try:
                            wellwritten = int(thumbody.find_element(By.CLASS_NAME, 'well-written').find_element(By.CLASS_NAME, 'num').get_attribute('textContent'))
                            if wellwritten == None:
                                wellwritten=0
                        except Exception as e:
                            wellwritten = 0
                        
                        if nice >= 0 or loveit >= 0 or wellwritten >= 0:
                            total_helpful_counts = nice + loveit + wellwritten
                        else:
                            total_helpful_counts = 0        
            
                        #Review Body
                        review_body = thumbody.find_element(By.CLASS_NAME, 'text').get_attribute('textContent').replace('\n','').replace('\r','').strip().replace('    ','').replace('  ...  ',' ')#.replace("\'","'")
            
                        print(f"""review_id: {review_id}, anime_id: {anime_id}, anime_name: {anime_name}, username, {username},
                        review_date: {review_date}, overall_rating: {overall_rating}, total_helpful_counts: {total_helpful_counts}""")    
                        
                        #Write into SQL database
                        try:
                            run_inserts(DB, insert_query,(
                                int(review_id), int(anime_id), anime_name, \
                                username, review_date, int(overall_rating), \
                                int(total_helpful_counts), review_body)
                            )
                            message=f'A review for "{anime_id}" has sucessfully be added to your database!'
                            send_message_to_custom_log(message,message_level=2)
                            
                        except Exception as e:
                            message=f'A review failed be added to your database! This occured on page "{url}". review_id={review_id} username={username}. Error : {e} Keep in mind this info may have errors, hence why it would not go into the data base'
                            send_message_to_custom_log(message,message_level=4)
                            pass
                    except:
                        time.sleep(10)
                        anime_id = titlebox.find_element(By.CLASS_NAME, 'title').get_attribute('href').split('/')[4]
            
                        #Review info
                        anime_name = titlebox.find_element(By.CLASS_NAME, 'title').get_attribute('textContent')
                        username = thumbody.find_element(By.CLASS_NAME, 'username').get_attribute('textContent').replace('\n','').replace(' ','')
                        review_date = thumbody.find_element(By.CLASS_NAME,'update_at').get_attribute('textContent')
            
                        #Review ratings
                        overall_rating = thumbody.find_element(By.CLASS_NAME, 'num').get_attribute('textContent')
            
            
                        #Review helpful counts - I considered a helpful responce as 'nice', 'love it', and 'well-written'.
                        # Use try except block if its blowing an error) to handle "nonexsistance" in the html
                        # Probably good practice for any pesky intermittent java ghosts
                        try:
                            nice = int(thumbody.find_element(By.CLASS_NAME, 'nice').find_element(By.CLASS_NAME, 'num').get_attribute('textContent')) 
                            if nice == None:
                                nice=0
                        except Exception as e:
                            nice = 0
                            #PUT A GOOD LOGGING STATMENT IN HERE! 
                            
                        try:
                            loveit = int(thumbody.find_element(By.CLASS_NAME, 'loveit').find_element(By.CLASS_NAME, 'num').get_attribute('textContent')) 
                            if loveit == None:
                                loveit=0
                        except Exception as e:
                            loveit = 0 
                            #PUT A GOOD LOGGING STATMENT IN HERE! 
                        
                        try:
                            wellwritten = int(thumbody.find_element(By.CLASS_NAME, 'well-written').find_element(By.CLASS_NAME, 'num').get_attribute('textContent'))
                            if wellwritten == None:
                                wellwritten=0
                        except Exception as e:
                            wellwritten = 0
                        
                        if nice >= 0 or loveit >= 0 or wellwritten >= 0:
                            total_helpful_counts = nice + loveit + wellwritten
                        else:
                            total_helpful_counts = 0
            
                        #Review Body
                        review_body = thumbody.find_element(By.CLASS_NAME, 'text').get_attribute('textContent').replace('\n','').replace('\r','').strip().replace('    ','').replace('  ...  ',' ')#.replace("\'","'")
            
                        print(f"""review_id: {review_id}, anime_id: {anime_id}, anime_name: {anime_name}, username, {username},
                        review_date: {review_date}, overall_rating: {overall_rating}, total_helpful_counts: {total_helpful_counts}""")    
                        
                        #Write into SQL database
                        try:
                            run_inserts(DB, insert_query,(
                                int(review_id), int(anime_id), anime_name, \
                                username, review_date, int(overall_rating), \
                                int(total_helpful_counts), review_body)
                            )
                            message=f'A review for "{anime_id}" has sucessfully be added to your database!'
                            send_message_to_custom_log(message,message_level=2)
                            
                        except Exception as e:
                            message=f'A review failed be added to your database! This occured on page "{url}". review_id={review_id} username={username}. Error : {e} Keep in mind this info may have errors, hence why it would not go into the data base'
                            send_message_to_custom_log(message,message_level=4)
                            pass
                        
            #Provide stats for monitoring
            current_time = time.time()
            elapsed_time = current_time - start_time
            requests = j + 1 - page_start
    
            print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
            print('Elapsed Time: {} minutes'.format(elapsed_time/60))
            if requests == page_end - page_start + 1:
                message='Review Scrape Complete!'
                send_message_to_custom_log(message,message_level=5)
                break
            print('Pausing...')
            time.sleep(random.uniform(sleep_min, sleep_max))
        #Note that there were no reviews on the page when you tried to access it the first time. (504s have happend, but also their last page is a 404 error page)
        else:
            message=f'No Review Container was seen on the page "{url}". A second attempt to reach that URL is being made. (Have seen 504 errors trying to reach later review pages)'
            send_message_to_custom_log(message,message_level=4)
            driver.implicitly_wait(30)
            driver.get(url)
            time.sleep(5)
            #Try to access the page the second time.  (504 errors have occured so for now we will try twice and then give up)
            if driver.find_element(By.CSS_SELECTOR, 'h1').get_attribute('textContent') ==  'Anime Reviews':
                review_containers = driver.find_elements(By.CLASS_NAME, 'review-element')
                
                #container=review_containers[1]        
                
                #Loops through the containers on a page
                for container in review_containers:
                    #Grab the title box for use with anime_id, anime_name, 
                    titlebox=container.find_elements(By.CSS_SELECTOR,'div')[0]
                    #Grab the main box where the main review body and lots of other usful info is held is held.
                    thumbody=container.find_elements(By.CSS_SELECTOR,'div')[1]
        
                    #Review Id (Primary Key)
                    review_id = thumbody.find_element(By.CLASS_NAME, 'btn-reaction').get_attribute('data-id')
                    
                    #Anime Id (Foreign Key)
                    anime_id = titlebox.find_element(By.CLASS_NAME, 'title').get_attribute('href').split('/')[4]
        
                    #Review info
                    anime_name = titlebox.find_element(By.CLASS_NAME, 'title').get_attribute('textContent')
                    username = thumbody.find_element(By.CLASS_NAME, 'username').get_attribute('textContent').replace('\n','').replace(' ','')
                    review_date = thumbody.find_element(By.CLASS_NAME,'update_at').get_attribute('textContent')
        
        
                    #Review ratings
                    overall_rating = thumbody.find_element(By.CLASS_NAME, 'num').get_attribute('textContent')
        
        
                    #Review helpful counts - I considered a helpful responce as 'nice', 'love it', and 'well-written'.
                    #There are a few other other tags that might be good to pull, and well written might be better off on its own.
                    try:
                        nice = int(thumbody.find_element(By.CLASS_NAME, 'nice').find_element(By.CLASS_NAME, 'num').get_attribute('textContent')) 
                        if nice == None:
                            nice=0
                    except Exception as e:
                        nice = 0
                        #PUT A GOOD LOGGING STATMENT IN HERE! 
                        
                    try:
                        loveit = int(thumbody.find_element(By.CLASS_NAME, 'loveit').find_element(By.CLASS_NAME, 'num').get_attribute('textContent')) 
                        if loveit == None:
                            loveit=0
                    except Exception as e:
                        loveit = 0 
                        #PUT A GOOD LOGGING STATMENT IN HERE! 
                    
                    try:
                        wellwritten = int(thumbody.find_element(By.CLASS_NAME, 'well-written').find_element(By.CLASS_NAME, 'num').get_attribute('textContent'))
                        if wellwritten == None:
                            wellwritten=0
                    except Exception as e:
                        wellwritten = 0
                    
                    if nice >= 0 or loveit >= 0 or wellwritten >= 0:
                        total_helpful_counts = nice + loveit + wellwritten
                    else:
                        total_helpful_counts = 0        
        
                    #Review Body
                    review_body = thumbody.find_element(By.CLASS_NAME, 'text').get_attribute('textContent').replace('\n','').replace('\r','').strip().replace('    ','').replace('  ...  ',' ')#.replace("\'","'")
        
                    print(f"""review_id: {review_id}, anime_id: {anime_id}, anime_name: {anime_name}, username, {username},
                    review_date: {review_date}, overall_rating: {overall_rating}, total_helpful_counts: {total_helpful_counts}""")    
                    
                    #Write into SQL database
                    try:
                        run_inserts(DB, insert_query,(
                            int(review_id), int(anime_id), anime_name, \
                            username, review_date, int(overall_rating), \
                            int(total_helpful_counts), review_body)
                        )
                        message=f'A review for "{anime_id}" has sucessfully be added to your database on the second try!'
                        send_message_to_custom_log(message,message_level=2)
                    except Exception as e:
                        message=f'A review failed be added to your database on the second URL load! This occured on page "{url}". review_id={review_id} username={username}. Error : {e}. Keep in mind this info may have errors, hence why it would not go into the data base'
                        send_message_to_custom_log(message,message_level=4)
                        pass
                
                #driver.close()
                
                #Provide stats for monitoring
                current_time = time.time()
                elapsed_time = current_time - start_time
                requests = j + 1 - page_start
        
                print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
                print('Elapsed Time: {} minutes'.format(elapsed_time/60))
                if requests == page_end - page_start + 1:
                    print('Scrape Complete')
                    break
                print('Pausing...')
                time.sleep(random.uniform(sleep_min, sleep_max))
            else:
                print('Scrape Complete')
                break                       # DO I NEED TO BREAK HERE?
    driver.close()
    message='Review Scrape Complete!'
    send_message_to_custom_log(message,message_level=5)



#%% update_animes_scrape
#How to figure out how many animes need to be scraped
#The entirety of the first anime scraper must have been run sucessfully before this works properly
#The large scale anime scrape goes by genre and not by anime ID numbers.  THIS IS BY ANIME ID
#This update scrape will be very slow as from the "Just Added" page, you will need to open each individual anime page.

# TODO : ADD LOGGING!!!!

def update_animes_scrape(DB=DB, sleep_min=9, sleep_max=18):
    
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
        # TODO : ADD A REAL USER AGENT!!! -----------------------------------------------------------------------------
        headers = {"User-Agent": "mal review scraper for research."}
        print('Scraping URLs to Scrape: {}'.format(url))
        
        try:
            response = get(url, headers=headers, timeout = 10)
        except:
            print('Request timeout')
            
        html_soup_initial = BeautifulSoup(response.text, 'html.parser')
        anime_links=html_soup_initial.find_all(class_='picSurround')
        print(len(anime_links))
        
        
        # TODO : DB CHECK FOR ANIME ID MOST RECENT.  Use most recent anime id to truncate the list somehow?
        
            
        ##############WHY IS THIS ONLY TRIGGERING ONCE?????
        
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
                except Exception as e:
                    print('Failed to insert into animes for anime_id: {0}, {1}'.format(anime_id, e))
                    pass
    
    
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
  
    
#%% Main `scrape_all()` function
# If the initial scrape crashes out for some reason, use the bypasses and genre index number to restart at a reasonable point.
# Dont use animes_page unless you are just looking to finish a particular genre...
def initial_scrape_all(studio_bypass = False, tag_bypass = False, animes_bypass = False, animes_page = 0, anime_genre_index = 0):
    #DB = 'anime7.db'
    
    #ALTHOUGH LOGICALLY THIS SHOULD FILE LOG DEBUG and INFO, BUT IT DOESN'T.  USE message_level 3 FOR SUPPRESSED MESSAGE, and 4 and 5 AS UNSUPRESSED ON THE LINE.
    rbint_custom_logger = create_custom_logger('NEWDATABASE_SECONDlongrun', clevel=4, flevel=1)

    DB=make_database()
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


#%% Update Scrape
def update_scrape(DB, willscrape_studios, willscrape_tags, willscrape_animes, willscrape_reviews):
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

 
#%% Database Check

def database_update_check(DB):
    '''
    Identifies what needs to be updated
    '''
    
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
        
        #input not working
        #print('Would you like to update your database of Studios? (Y/N)')
        
        #Ask whether you want to scrape studios and outputs a variable to control whether it scrapes.
        #THIS CAN JUST BE DUPLICATED AT THE END OF EACH CHECK IF UP TO DATE PORTION.  Result will call scrape.
        # MAYBE THE CALL WOULD BE BETTER WITH A NEEDSSCRAPE and a WILLSCRAPE variable.
        
        
        
        # MAKE IT BASIC, and use this as an individual function(object)
        # studios_desire=''
        # while studios_desire != 'y' or 'n':
        #     studios_desire=input('Would you like to update your database of Studios? (Y/N) \nIf you say no here and yes to a later update, you will have Animes and Reviews fail to be added to your database due to the Studios being a Primary Key!\n')
        #     #Why does this not sasisfy the while statement?
        #     studios_desire=studios_desire.lower()[0]
        # if studios_desire == 'y':
        #     willscrape_studios = True
        # else:
        #     willscrape_studios = False
            
    
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
        response = get(url, headers=headers, timeout = 10)
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
    
    # I could add a scrape of the new Tag here, but it may not be worth it.
    # Figure out how many animes have been added since you last scraped.  
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

       