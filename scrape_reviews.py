# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:22:27 2022

@author: Robert
"""
#%%
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from sql_queries import run_inserts, run_query
from rb_custom_logger import send_message_to_custom_log
from useful_functions import round_up, round_down
import random


#
DB='some_database.db'
#%% scrape_reviews

def scrape_reviews(DB=DB, sleep_min=0, sleep_max=10):
    
    """
    scrape_animes(DB=DB, ..., sleep_min=9, sleep_max=18)
    
    Crawls through the anime review pages to scrape and insert review information into database.
    
    DB: Name of Database for updating (requires the '.db').
    
    Optional keyword arguments:
    sleep_min: An interger argument used to represent the minimum time in seconds for randomize the pause time before moving between pages.
    sleep_max: An interger argument used to represent the maximum time in seconds for randomize the pause time before moving between pages.
    """
    
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


