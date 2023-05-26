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

# Set Host URL and API-Key
host_url = 'https://<YOUR RADARR ADDRESS HERE>/'

# You can find your API key in Settings > General.
api_key = '<YOUR API KEY HERE>'

# How long should the release be in the queue, before it gets replaced.
time_limit = tdelta(hours=0, days=1)

# Logging
log_file = './RadarrStalledCleaner.log'



def module_logger():
    logger = logging.getLogger(__name__)
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_file, when='D', interval=1, backupCount=30)
    formatter = logging.Formatter(u'%(asctime)s %(levelname)-8s %(message)s')
    formatter.datefmt = '%Y-%m-%d %H:%M:%S'
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def main(args):

    # Logging
    log = module_logger()
    log.setLevel(logging.DEBUG)
    
    # Instantiate RadarrAPI Object
    try:
        radarr = RadarrAPI(host_url, api_key)
    except requests.ConnectionError as e:
        log.fatal('Unable to connect to server: %s', e)
        return 1
    except requests.exceptions.SSLError as e:
        log.fatal('SSL error %s', e)
        return 1
    except requests.RequestException as e:
        log.fatal('Unable to connect: %s', e)
        return 1
    except Exception as e:
        log.fatal('Unhandled exception: %s', e)
        return 1
        
    queued_movies = []
    # Get all movies in download queue (Activity tab).
    try:
        queued_movies = radarr.get_queue_details()
    except requests.ConnectionError as e:
        log.fatal('Unable to connect to server (Is the API key correct?): %s', e)
        return 1
    except requests.exceptions.SSLError as e:
        log.fatal('SSL error %s', e)
        return 1
    except requests.RequestException as e:
        log.fatal('Unable to connect: %s', e)
        return 1
    except Exception as e:
        log.fatal('Unhandled exception: %s', e)
        return 1
    
    log.debug("Connected.")

    for movie_download in queued_movies:

        # Ignore movie if it is not being downloaded.
        if movie_download['status'] != 'downloading':
            log.info('Skipping "%s" - Status "%s" is not a downloading status.',
                         movie_download['title'], movie_download['status'])
            continue

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
            log.info('Removing stale movie download: %s', movie_download['title'] )
            
            log.debug('Removing stale movie title: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                           movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])
            

            resp = requests.Response()
            try:
                resp = radarr.del_queue(movie_download['id'],True,True)
            except BaseException as e:
                log.critical('Error when removing from queue: %s', e)
                continue
            
            if resp.status_code != 200:    
                log.error('Error removing stale movie: "%s"', movie_download['title'])
                log.debug('Error: %s', resp)
            else:
                log.info('Removed stale movie download: ', movie_download['title'] )           
                log.debug('Removed stale movie title: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                           movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])


if __name__ == '__main__':
    main(sys.argv)
