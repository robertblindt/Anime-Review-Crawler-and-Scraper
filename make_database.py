# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:05:41 2022

@author: Robert
"""
#%%
from sql_queries import run_command
from rb_custom_logger import send_message_to_custom_log

#%% make database
def make_database():
    
    """
    initial_scrape_all()
    
    Requests a user string input to create a database and (or if the database already exsists, just) pass the name into the namespace. 
    """
    
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
        
    
