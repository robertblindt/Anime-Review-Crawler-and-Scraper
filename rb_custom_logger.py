# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 09:52:32 2022

Functions: 
    create_custom_logger(logger_name, clevel=3, flevel=3)
    
    send_message_to_custom_log(message, custom_logger, level='warning')
        Sets the level type for the log file
    
----------
logger_name : TYPE
    DESCRIPTION.
clevel : TYPE, optional
    DESCRIPTION. The default is 3.
flevel : TYPE, optional
    DESCRIPTION. The default is 3.

Returns
-------
custom_logger : TYPE
    DESCRIPTION.

@author: Robert
"""

import logging
clevel = int 
flevel = int 

#%% create_custom_logger
#FOR SOME REASON clevel AND flevel DONT GET PASSED INTO THE IF STATEMENT? 
# If clevel is 4 or 5, it suppressed a caller of warning, and only prints Error and Critical on the console. 
# flevel always suppresses info or debug even when called as a 1.  V Confused...

def create_custom_logger(logger_name, clevel = clevel, flevel = flevel):
    
    """
    create_custom_logger(logger_name, clevel = clevel, flevel = flevel)
    
    Creates a log file using the required 'logger_name'. '.log' should not be used in the name
    
    clevel: The console logging level to be allowed through from an indexed list - ['INFO','DEBUG','WARNING','ERROR','CRITICAL']
    flevel: The file logging level to be allowed through from an indexed list - ['INFO','DEBUG','WARNING','ERROR','CRITICAL']
    """

    
    
    #maybe just use intergers to get levels?
    if clevel >= 1 and clevel <= 5 and flevel >= 1 and flevel <= 5:
        
        my_custom_logger = logging.getLogger(__name__)
        
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(f'{logger_name}.log')
        
        my_custom_logger.setLevel(logging.DEBUG)
        
        if clevel == 1:
            c_handler.setLevel(logging.DEBUG)
            
        elif clevel == 2:
            c_handler.setLevel(logging.INFO) 
            
        elif clevel == 3:
            c_handler.setLevel(logging.WARNING) 
            
        elif clevel == 4:
            c_handler.setLevel(logging.ERROR)
            
        else:
            c_handler.setLevel(logging.CRITICAL)
            
        
        if flevel == 1:
            f_handler.setLevel(logging.DEBUG) 
            
        elif flevel == 2:
            f_handler.setLevel(logging.INFO)
            
        elif flevel == 3:
            f_handler.setLevel(logging.WARNING)  
            
        elif flevel == 4:
            f_handler.setLevel(logging.ERROR)
            
        else:
            f_handler.setLevel(logging.CRITICAL)  
        
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        
        my_custom_logger.addHandler(c_handler)
        my_custom_logger.addHandler(f_handler)
        
        
        return my_custom_logger 
    
    else:
        print('INVALID LEVEL GIVEN!  PLEASE CHECK THE INPUT FOR "clevel" and "flevel"!  VALID INPUTS ARE 1-5')
        

#%% to make the below function not throw errors, create temp variables.
# CURRENTLY Flogs only down to 3 instead of 1, and clevel seems to work from the defaults.  If you do it in 'syntax' it breaks though... IDK why
logger_name = 'NOVEMBER172022_002'
clevel=4
flevel=1
my_custom_logger = create_custom_logger(logger_name,clevel=clevel,flevel = flevel)
#This is here to test out the restult of trying to add different log levels


        
#logging.basicConfig(filename='TESTLOGBECAUSEICANTDOANEVALSPRINTF.log', level=logging.INFO)

#%% send_message_to_custom_log
#create a message variable using f string formatting. message = f'The database failed to insert {anime_id}. Error message {e}'
message_level = 1
def send_message_to_custom_log(message, message_level = message_level, custom_logger = my_custom_logger):
    
    """
    send_message_to_custom_log(message, message_level = message_level, ..., custom_logger = my_custom_logger)
    
    Sends a log message to the custom log message of level 'message_level' from an indexed list - ['info', 'debug', 'warning', 'error', 'critical']
    
    Optional keyword arguments:
    custom_logger: The variable name used to communicate with the logger.  
    It's default name is not very intuative because I was tyring to avoid the built in logger names, so this should probalby be fixed early onto continued development to be more readable.
    """
    
    
    if message_level == 1:
        custom_logger.debug(message)
        
    elif message_level == 2:
        custom_logger.info(message)
        
    elif message_level == 3:
        custom_logger.warning(message)
        
    elif message_level == 4:
        custom_logger.error(message)
        
    elif message_level == 5:
        custom_logger.critical(message)
        
    else:
        print('INVALID INPUT')

#%%
send_message_to_custom_log('message_5', message_level = 5)      


#%% EVEN THE EXAMPLE DOESNT WORK WITH LOWER LEVELS...  Am I misunderstanding something fundimental?
# # Create a custom logger
# logger = logging.getLogger(__name__)

# # Create handlers
# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler('file_67.log')
# c_handler.setLevel(logging.DEBUG)
# f_handler.setLevel(logging.DEBUG)

# # Create formatters and add it to handlers
# c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)

# # Add handlers to the logger
# logger.addHandler(c_handler)
# logger.addHandler(f_handler)

# logger.warning('This is a warning')
# logger.error('This is an error')
# logger.info('infoTry')
# logger.debug('debugmaybe?')


#%%
import logging
#import auxiliary_module

# create logger with 'spam_application'
logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.debug('creating an instance of auxiliary_module.Auxiliary')
#a = auxiliary_module.Auxiliary()
logger.info('created an instance of auxiliary_module.Auxiliary')
logger.warning('calling auxiliary_module.Auxiliary.do_something')
#a.do_something()
logger.error('finished auxiliary_module.Auxiliary.do_something')
logger.critical('calling auxiliary_module.some_function()')
#auxiliary_module.some_function()
logger.critical('done with auxiliary_module.some_function()')