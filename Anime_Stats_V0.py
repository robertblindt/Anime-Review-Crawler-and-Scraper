# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 11:07:28 2022

@author: Robert
"""
#%%
import sqlite3
import pandas as pd
#import math
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#%%

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

#%%
DB = 'NEWDATABASE_secondlongrun.db'

#%%

testq = '''
SELECT 
    t.tag_id tag_id,
    t.tag_name Genre,
    a.anime_id,
    a.overall_rating
FROM animes a
INNER JOIN anime_tags at ON a.anime_id = at.anime_id
INNER JOIN tags t ON at.tag_id = t.tag_id

'''

table1 = run_query(DB, testq)
table1.head()


#%%
#Handle null values
table1['overall_rating_std'] = pd.to_numeric(table1['overall_rating'], errors='coerce').dropna()
table1['overall_rating_mean'] = pd.to_numeric(table1['overall_rating'], errors='coerce').dropna()
table1['sample_size'] = 0

table1_cleaned = table1.groupby(['tag_id', 'Genre'], as_index = False).agg({'overall_rating_std': np.std, 'overall_rating_mean': np.mean, 'sample_size': len})
table1_cleaned = table1_cleaned.sort_values(by=['overall_rating_mean'], ascending = False).head(10)
table1_cleaned


#%% top rated Genres
y = table1_cleaned['Genre']
x = table1_cleaned['overall_rating_mean']
std = table1_cleaned['overall_rating_std']
xerr = 1.96*std/np.sqrt(table1_cleaned['sample_size']).values

fig = plt.figure(figsize=(10,5))
ax = sns.barplot(x=x, y=y, xerr=xerr, palette = 'viridis')
ax.set_xlabel('Average Rating')
plt.show()


#%% Does # Genres impact the rating?
q2 = '''
WITH anime_genre_counts AS
    (SELECT
        a.anime_id,
        COUNT(at.anime_id) Number_of_genres,
        AVG(a.overall_rating) overall_rating
    FROM animes a
    INNER JOIN anime_tags at ON a.anime_id = at.anime_id
    INNER JOIN tags t ON at.tag_id = t.tag_id
    GROUP BY 1
    )

SELECT
    Number_of_genres,
    COUNT(anime_id) sample_size,
    AVG(overall_rating) Average_rating
FROM anime_genre_counts
GROUP BY 1
ORDER BY 3 DESC
'''

table2 = run_query(DB, q2)
table2



#%% 10 Best Studio for longer format animes (Minimum 10 episode shows used as sample)
q3 = '''
WITH anime_studios AS
    (SELECT
        s.studio_name,
        COUNT(a.anime_id) animes_produced,
        AVG(a.overall_rating) overall_rating,
        episodes_total
    FROM animes a
    INNER JOIN studios s ON s.studio_id = a.studio_id
    WHERE episodes_total > 10
    GROUP BY 1
    )

SELECT
    studio_name,
    animes_produced,
    overall_rating average_ratings
FROM anime_studios
WHERE animes_produced > 10
ORDER BY average_ratings DESC
LIMIT 10
'''

table3 = run_query(DB, q3)
table3


#%% What is the 10 best source for an anime?
q4 = '''
SELECT
    source_material,
    COUNT(anime_id) sample_size,
    AVG(overall_rating) average_ratings
FROM animes
GROUP BY source_material
ORDER BY average_ratings DESC
LIMIT 10
'''

table4 = run_query(DB, q4)
table4

#%%
y = table4['source_material']
x = table4['average_ratings']

fig = plt.figure(figsize=(10,5))
ax = sns.barplot(x=x, y=y, palette='viridis')
ax.set_xlabel('Average Rating')
ax.set_ylabel('Source Material')
ax.set_title('Anime Source Material vs. Anime Rating')

plt.show()



