# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:01:37 2022

@author: Robert
"""

#%% Imports
import sqlite3
import pandas as pd


#%% PRODUCTION Interface for SQLite database

def run_query(DB, q):
    """
    run_query(DB, q)
    
    Requests a read call from a database.
    
    DB: Name of Database for updating (requires the '.db').
    q: SQL query command
    """
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)

def run_command(DB, c):
    """
    run_command(DB, c)
    
    Sends a command to the databse.
    
    DB: Name of Database for updating (requires the '.db').
    c: SQL command
    """
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c)

# PRAGMA foreign_keys = OFF seems to be the wrong choice for enforcing foreign_key contraints, but there is an
# inexplicable failure on entire pages for seemingly no good reason in the "anime_scrape" scripts. 
def run_inserts(DB, c, values):
    """
    run_insert(DB, c, values)
    
    Sends a command to the databse to insert a piece of data into the database.
    
    DB: Name of Database for updating (requires the '.db').
    c: SQL command
    value: Information to be inserted into the database in the required format.
    """
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = OFF;')
        conn.isolation_level = None
        conn.execute(c, values)
