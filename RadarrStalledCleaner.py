'''
 encoding: UTF-8
 python: 3.9.13

 Author: Dako Dimov
 Date: 21.04.2023 (v1.0)    - Initial release.
 Date: 02.05.2023 (v1.1)    - Added logging and fixed items with no download events.
 Date: 26.05.2023 (v1.2)    - Fixed logging errors that are not errors and added log file rotation.
 
 Version: 1.2
'''

# Import RadarrAPI Class
from pyarr import RadarrAPI
from datetime import datetime as dt
from datetime import timedelta as tdelta

import logging
import logging.handlers
import sys
import requests
import os
import configparser

# How long should the release be in the queue, before it gets replaced.
time_limit = tdelta(hours=0, days=1, minutes=0, weeks=0)

# How long should a release stay blocked, before being unblocked.
blocked_release_time_limit = tdelta(hours=0, days=30, minutes=0, weeks=0)

# Read config
try:
    config = configparser.ConfigParser()
    res = config.read('./config.ini')
    
    # Set config values
    host_url = config['radarr']['host_url']
    urlbase = config['radarr']['url_base']
    api_key = config['radarr']['api_key']
    log_level = config['radarr']['log_level'].upper()
    log_file = config['radarr']['log_file']
    blocklist_cleanup = config.getboolean('radarr','blocklist_cleanup')
    if blocklist_cleanup:
        days = 30
        try:
            days = int(config['radarr']['blocklist_cleanup_max_age_days'])
        except ValueError as e:
            print('Invalid value for blocklist max age in days. Using default '+str(days)+' days. ', e, file=sys.stderr)
  
        blocked_release_time_limit = tdelta(days=days)
        
    if urlbase != "": 
        host_url = "{}{}".format(host_url,urlbase)
    
except configparser.Error as e:
    print('Error: ', e, file=sys.stderr)
    sys.exit(1)
except KeyError as e:
    print('Error: key not found -', e, file=sys.stderr)
    sys.exit(1)
    


def module_logger() -> logging.Logger:
    
    # Try to create log directory.
    try:
        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except:
        # If we can't create the directory, the logging handler initialisation will handle it.
        pass
    
    logger = logging.getLogger(__name__)
    handler = logging.NullHandler()
    
    try:
        handler = logging.handlers.TimedRotatingFileHandler(filename=log_file, when='D', interval=1, backupCount=30)
    except Exception as e:
        print("Unable to create log file. Continuing with logging to stderr.\n", e, file=sys.stderr)
        handler = logging.StreamHandler()
        
    formatter = logging.Formatter(u'%(asctime)s %(levelname)-8s %(message)s')
    formatter.datefmt = '%Y-%m-%d %H:%M:%S'
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    try:
        logger.setLevel(logging.getLevelName(log_level))
    except:
        logger.setLevel(logging.NOTSET)
        logger.warning('Invalid logging level "' + log_level + '". Using default level "' + logging.getLevelName(logger.getEffectiveLevel()) + '".')        
        
    return logger

def blocklist_cleaner(radarr_api:RadarrAPI, log:logging.Logger):
    page = 1
    page_size = 500
    remaining_records = 1

    ids_to_unblock = []

    
    while remaining_records > 0:
        
        try:
            blocked_releases = radarr_api.get_blocklist(page=page,page_size=page_size, sort_key='date', sort_dir='ascending')
            log.debug('Got {} total releases. Page size: {}. Current page: {}.', blocked_releases['totalRecords'],
                      page_size, page)
        except requests.Timeout:
            # Maybe the request is too big. Try decreasing the page size.
            if page_size > 0:
                log.warn('Request timed out. Reducing page size from {} to {}.', page_size, page_size/2)
                page_size/=2
                continue
            else:
                # Page size can not be decreased any further. Aborting.
                log.error('Request timed out. Can not reduce page size. (Current: {})', page_size)
                return 1
        
        if page == 1:
            # Get the total count of records the first time.
            remaining_records = blocked_releases['totalRecords']
            
        
        remaining_records -= page*page_size
    
        # Add ID if it should be unblocked.
        for release in blocked_releases:
            time_elapsed = dt.now() - dt.strptime(release['date'], '%Y-%m-%dT%H:%M:%SZ')
            if time_elapsed >= blocked_release_time_limit:
                ids_to_unblock.append(release['id'])
                log.debug('Added blocklist ID: {}, blocked {} ago.', release['id'], time_elapsed)
            else:
                # The records are sorted by date. If this record has
                # not reached the limit, the following ones also wouldn't.
                log.debug('Skipping blocklist ID: {}, blocked {} ago. (Limit not reached. Skipping all other entries.)', release['id'], time_elapsed)
                remaining_records = 0
                break
        
        page+=1


    # If there are records for unblocking, send the API call.
    if len(ids_to_unblock) > 0:
        resp = requests.Response()
        
        try:
            resp = radarr_api.del_blocklist_bulk(ids_to_unblock)
        except Exception as e:
            log.critical('Error when removing from blocklist: %s', e)

        if resp.status_code != 200:    
            log.error('Error removing blocked releases: {%s}', ', '.join(str(x) for x in ids_to_unblock) )
            log.debug('Error: %s', resp)
        else:
            log.info('Removed old releases blocklist entries.' )           
            log.debug('Removed old releases blocklist entries: {%s}', ', '.join(str(x) for x in ids_to_unblock) )

def main(args):

    # Logging
    log = module_logger()
    log.info('Started.')
    
    # Instantiate RadarrAPI Object
    try:
        radarr = RadarrAPI(host_url, api_key)
    except requests.exceptions.SSLError as e:
        log.fatal('SSL error: %s', e)
        return 1
    except requests.ConnectionError as e:
        log.fatal('Unable to connect to server: %s', e)
        return 1
    except requests.RequestException as e:
        log.fatal('Unable to connect: %s', e)
        return 1
    except Exception as e:
        log.fatal('Unhandled exception: %s', e, exc_info=1)
        return 1

    queued_movies = []
    # Get all movies in download queue (Activity tab).
    try:
        queued_movies = radarr.get_queue_details()
    except requests.exceptions.SSLError as e:
        log.fatal('SSL error: %s', e)
        return 1
    except requests.ConnectionError as e:
        log.fatal('Unable to connect to server (Is the API key correct?): %s', e)
        return 1
    except requests.RequestException as e:
        log.fatal('Unable to connect: %s', e)
        return 1
    except Exception as e:
        log.fatal('Unhandled exception: %s', e, exc_info=1)
        return 1
    
    log.debug("Connected.")

    total_movies_in_queue = len(queued_movies)
    total_downloading_movies = 0
    total_movies_to_remove = 0
    total_movies_removed = 0

    for movie_download in queued_movies:

        # Ignore movie if it is not being downloaded.
        if movie_download['status'] != 'downloading':
            log.info('Skipping "%s" - Status "%s" is not a downloading status.',
                         movie_download['title'], movie_download['status'])
            continue
        
        total_downloading_movies+=1
        
        # Get when the movie was grabbed.
        grab_events = radarr.get_movie_history(movie_download['movieId'], 'grabbed')

        if len(grab_events) <= 0:
            # log error
            log.error('Movie "%s" has no history of being grabbed.', movie_download['title'])
            continue

        # Sort by grab date.
        grab_events.sort(key=lambda event: event['date'],reverse=True)
        last_grab_event = grab_events[0]
        
        # Debug print
        for evt in grab_events:
            time_delta = dt.now() - dt.strptime(evt['date'], '%Y-%m-%dT%H:%M:%SZ')
            log.debug('%s --- %s --- %s', evt['date'], movie_download['title'], time_delta)
        
        # Get time elapsed from last grab.
        time_elapsed = dt.now() - dt.strptime(last_grab_event['date'], '%Y-%m-%dT%H:%M:%SZ')

        if time_elapsed > time_limit:
            
            total_movies_to_remove+=1
            
            log.info('Removing stale movie download: %s', movie_download['title'] )
            
            log.debug('Removing stale movie title: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                           movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])
            

            resp = requests.Response()
            try:
                resp = radarr.del_queue(movie_download['id'],True,True)
            except Exception as e:
                log.critical('Error when removing from queue: %s', e)
                continue
            
            if resp.status_code != 200:    
                log.error('Error removing stale movie: "%s"', movie_download['title'])
                log.debug('Error: %s', resp)
            else:
                log.info('Removed stale movie download: ', movie_download['title'] )           
                log.debug('Removed stale movie title: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                           movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])
                total_movies_removed+=1

    if blocklist_cleanup:
        blocklist_cleaner(radarr, log)

    log.info("Summary:\
            Total movies in queue: {} \
            Total downloading: {} \
            Total to remove: {} \
            Total removed: {}",
            total_movies_in_queue,
            total_downloading_movies,
            total_movies_to_remove,
            total_movies_removed)

if __name__ == '__main__':
    main(sys.argv)
