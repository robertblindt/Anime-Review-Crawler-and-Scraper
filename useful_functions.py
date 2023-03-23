# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:04:20 2022

@author: Robert
"""
import math

#%% Useful Functions
#Needed for the estimations!
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier
