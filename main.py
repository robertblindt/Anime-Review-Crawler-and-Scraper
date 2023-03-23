# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 10:52:24 2022

@author: Robert
"""
#%%
from make_database import make_database
from initial_scrape_all import initial_scrape_all
from database_update_check_and_update import database_update_check_and_update


#%%
def main():
    '''
    main()
    
    Requests input to call the two functions that run each scraper. Only allows a 'q', 1, or 2 as an input to run.

    '''
    scrape_choice = ''
    while scrape_choice != 'q' :
        print('Enter q to quit.')
        scrape_choice = input('Would you like to instantiate your database and do the initia scrape (1), or update your database(2)? (1 or 2)\n')
    
        if scrape_choice == '1':
            DB=make_database()
            initial_scrape_all(DB = DB, studio_bypass = False, tag_bypass = False, animes_bypass = False, animes_page = 0, anime_genre_index = 0)
            
        elif scrape_choice == '2':
            DB=make_database()
            database_update_check_and_update(DB)
        
        elif scrape_choice == 'q':
            break
        
        else:
            print("Please enter 1 or 2 to run a scraper or q to quit.")
            
            
